from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from agno_deep_agents import DeepAgentConfig, DeepAgentMedia, create_deep_agent, run_deep_agent
from agno_deep_agents.acp_server import run_acp_server


AGNO_COLORS = {
    "primary": "\033[38;2;0;202;190m",
    "accent": "\033[38;2;95;220;140m",
    "muted": "\033[38;2;130;148;170m",
    "warning": "\033[38;2;245;170;70m",
    "error": "\033[38;2;245;95;95m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)

    # Subcommands (pattern: agdeep acp ...)
    if argv and argv[0] == "acp":
        return _parse_acp_args(argv[1:])

    # Historical alias: `news ...` should behave like the default "run" command
    # when invoked as `agno-deep-agent news ...`.
    if argv and argv[0] == "news":
        argv = argv[1:]

    return _parse_run_args(argv)


def _parse_run_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agno-deep-agent",
        description="Run an Agno-native Deep Agent CLI with teams, memory, skills, compression, and multimodal input.",
    )
    parser.set_defaults(command="run")
    parser.add_argument(
        "task",
        nargs="*",
        help=(
            "Task to run. If omitted in a TTY, an interactive Agno-colored session starts. "
            "If stdin is piped, stdin is combined with this task."
        ),
    )
    parser.add_argument(
        "-p",
        "--prompt",
        action="append",
        default=[],
        help="Prompt text to append to piped stdin or positional task. Can be repeated.",
    )
    _add_common_options(parser, include_session_id=True)
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Require a single task from args or stdin instead of opening the interactive CLI.",
    )
    parser.add_argument(
        "--no-stream",
        "--quiet-stream",
        action="store_true",
        help="Print the final response after completion instead of streaming.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Clean output for piping: hide member responses and buffer the final answer.",
    )
    parser.add_argument(
        "--hide-members",
        "--hide-agents",
        action="store_true",
        help="Hide specialist member responses in the console output.",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Attach an image path or URL. Can be repeated.",
    )
    parser.add_argument(
        "--audio",
        action="append",
        default=[],
        help="Attach an audio path or URL. Can be repeated.",
    )
    parser.add_argument(
        "--video",
        action="append",
        default=[],
        help="Attach a video path or URL. Can be repeated; model support varies.",
    )
    parser.add_argument(
        "--file",
        dest="files",
        action="append",
        default=[],
        help="Attach a document/file path or URL. Can be repeated.",
    )
    parser.add_argument(
        "--startup-cmd",
        default=None,
        help="Run a local command once before the first prompt. Output is shown but not injected.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable Agno-colored interactive UI text.",
    )
    return parser.parse_args(argv)


def _parse_acp_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agno-deep-agent acp",
        description="Run Agno Deep Agent as an ACP stdio server for editors and IDEs.",
    )
    parser.set_defaults(command="acp", no_stream=True, hide_members=True, quiet=False)
    _add_common_options(parser, include_session_id=False)
    return parser.parse_args(argv)


def _add_common_options(parser: argparse.ArgumentParser, *, include_session_id: bool) -> None:
    # Aliases: keep long flags stable, add short/alternate forms.
    # Backward compatibility: existing flags keep working unchanged.
    parser.add_argument(
        "-w",
        "--workspace",
        "--workdir",
        default=os.getenv("DEEP_AGENT_WORKSPACE", "."),
        help="Workspace root for file and shell tools.",
    )
    parser.add_argument(
        "--db-file",
        "--db",
        default=None,
        help="SQLite database path for sessions, memory, and learning.",
    )
    parser.add_argument(
        "--skills-dir",
        "--skills",
        default=None,
        help="Directory containing Agno skills. Defaults to ./skills.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=os.getenv("DEEP_AGENT_MODEL", "openai-responses:gpt-5.2"),
        help="Model spec, for example openai-responses:gpt-5.2 or ollama:devstral-2.",
    )
    parser.add_argument(
        "--ollama-host",
        "--ollama-url",
        default=os.getenv("OLLAMA_HOST"),
        help="Optional Ollama host, for example http://localhost:11434.",
    )
    parser.add_argument(
        "-u",
        "--user-id",
        "--user",
        default=os.getenv("DEEP_AGENT_USER_ID"),
        help="Stable user id for memory.",
    )
    if include_session_id:
        parser.add_argument(
            "-s",
            "--session-id",
            "--session",
            default=os.getenv("DEEP_AGENT_SESSION_ID"),
            help="Stable session id for continuing a task.",
        )
    parser.add_argument(
        "-n",
        "--max-iterations",
        "--max-iter",
        "--max-turns",
        type=int,
        default=int(os.getenv("DEEP_AGENT_MAX_ITERATIONS", "8")),
        help="Maximum task-loop iterations for the team.",
    )
    parser.add_argument(
        "--no-shell",
        "--no-exec",
        action="store_true",
        help="Disable shell execution while keeping filesystem tools enabled.",
    )
    parser.add_argument(
        "-S",
        "--shell-allow-list",
        default=os.getenv("DEEP_AGENT_SHELL_ALLOW_LIST"),
        help=(
            "Comma-separated shell command allow-list, 'recommended' for defaults, "
            "or 'all' to disable command-name filtering."
        ),
    )
    parser.add_argument(
        "--no-compression",
        action="store_true",
        help="Disable Agno context compression for tool results.",
    )
    parser.add_argument(
        "--compression-model",
        default=None,
        help="Optional cheaper/faster model spec used only for tool-result compression.",
    )
    parser.add_argument(
        "--compression-limit",
        type=int,
        default=None,
        help="Compress after this many uncompressed tool results. Defaults to 3.",
    )
    parser.add_argument(
        "--compression-token-limit",
        type=int,
        default=None,
        help="Compress when model-counted context reaches this token threshold.",
    )
    parser.add_argument(
        "--no-send-media",
        action="store_true",
        help="Store media metadata but do not send attached media to the model.",
    )
    parser.add_argument(
        "--no-store-media",
        action="store_true",
        help="Do not store attached media in Agno session storage.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable Agno debug mode.",
    )


def main() -> int:
    args = parse_args()
    config = _build_config(args)

    uses_openai = ":" not in args.model or args.model.startswith(("openai:", "openai-responses:", "responses:"))
    if uses_openai and not os.getenv("OPENAI_API_KEY"):
        print(
            "Warning: OPENAI_API_KEY is not set; the run will fail when the model is called.",
            file=sys.stderr,
        )

    if args.command == "acp":
        return run_acp_server(config, user_id=args.user_id)

    media = _build_cli_media(args)
    if args.startup_cmd:
        _run_startup_command(args.startup_cmd, config, color=_use_color(args))

    task = _read_task(args)
    if not task and sys.stdin.isatty() and not args.non_interactive:
        return _run_interactive(
            config,
            user_id=args.user_id,
            session_id=args.session_id,
            pending_media=media,
            use_color=_use_color(args),
        )

    if not task:
        print("Provide a task as an argument or through stdin.", file=sys.stderr)
        return 2

    try:
        run_deep_agent(
            task,
            config,
            stream=not (args.no_stream or args.quiet),
            user_id=args.user_id,
            session_id=args.session_id,
            media=media,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def _build_config(args: argparse.Namespace) -> DeepAgentConfig:
    config_kwargs: dict[str, object] = {
        "workspace": Path(args.workspace),
        "db_file": Path(args.db_file) if args.db_file else None,
        "skills_dir": Path(args.skills_dir) if args.skills_dir else None,
        "model": args.model,
        "ollama_host": args.ollama_host,
        "enable_shell": not args.no_shell,
        "max_iterations": args.max_iterations,
        "debug_mode": args.debug,
        "show_members_responses": not (getattr(args, "hide_members", False) or getattr(args, "quiet", False)),
    }

    if args.no_send_media:
        config_kwargs["send_media_to_model"] = False
    if args.no_store_media:
        config_kwargs["store_media"] = False

    shell_allow_list = _parse_shell_allow_list(args.shell_allow_list)
    if shell_allow_list is not None:
        allowed_commands, allow_all = shell_allow_list
        config_kwargs["allowed_shell_commands"] = allowed_commands
        config_kwargs["allow_all_shell_commands"] = allow_all

    if args.no_compression:
        config_kwargs["compress_tool_results"] = False
    if args.compression_model:
        config_kwargs["compression_model"] = args.compression_model
        config_kwargs["compress_tool_results"] = True
    if args.compression_limit is not None:
        config_kwargs["compression_tool_results_limit"] = args.compression_limit
        config_kwargs["compress_tool_results"] = True
    if args.compression_token_limit is not None:
        config_kwargs["compression_token_limit"] = args.compression_token_limit
        config_kwargs["compress_tool_results"] = True

    return DeepAgentConfig(**config_kwargs)


def _parse_shell_allow_list(value: str | None) -> tuple[tuple[str, ...], bool] | None:
    if value is None or not value.strip():
        return None

    normalized = value.strip().lower()
    if normalized == "recommended":
        return None
    if normalized == "all":
        return (), True

    commands = tuple(command.strip() for command in value.split(",") if command.strip())
    if not commands:
        return None
    return commands, False


def _build_cli_media(args: argparse.Namespace) -> DeepAgentMedia:
    return DeepAgentMedia(
        images=tuple(args.image),
        audio=tuple(args.audio),
        videos=tuple(args.video),
        files=tuple(args.files),
    )


def _read_task(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if not sys.stdin.isatty():
        stdin_text = sys.stdin.read().strip()
        if stdin_text:
            parts.append(stdin_text)
    parts.extend(prompt.strip() for prompt in args.prompt if prompt.strip())
    arg_task = " ".join(args.task).strip()
    if arg_task:
        parts.append(arg_task)
    return "\n\n".join(parts).strip()


def _run_startup_command(command: str, config: DeepAgentConfig, *, color: bool) -> None:
    if not config.enable_shell:
        print(_paint("startup command skipped because --no-shell is set", "warning", color), file=sys.stderr)
        return

    print(_paint(f"$ {command}", "muted", color), file=sys.stderr)
    try:
        completed = subprocess.run(
            command,
            cwd=config.resolved_workspace,
            shell=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print(_paint("startup command timed out after 60s", "warning", color), file=sys.stderr)
        return
    except OSError as exc:
        print(_paint(f"startup command failed: {exc}", "warning", color), file=sys.stderr)
        return

    if completed.returncode != 0:
        print(
            _paint(f"startup command exited with code {completed.returncode}; continuing", "warning", color),
            file=sys.stderr,
        )


def _run_interactive(
    config: DeepAgentConfig,
    *,
    user_id: str | None,
    session_id: str | None,
    pending_media: DeepAgentMedia,
    use_color: bool,
) -> int:
    active_session_id = session_id or f"cli-{uuid4().hex[:8]}"
    team = create_deep_agent(config)
    _print_banner(config, active_session_id, pending_media, use_color)

    while True:
        try:
            prompt = input(_paint("agdeep", "primary", use_color) + _paint(" > ", "muted", use_color))
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print(_paint("\nUse /quit to exit, or keep typing a new prompt.", "warning", use_color))
            continue

        prompt = prompt.strip()
        if not prompt:
            continue

        if prompt.startswith("/"):
            result = _handle_interactive_command(prompt, config, team, active_session_id, pending_media, use_color)
            if result is None:
                return 0
            config, team, active_session_id, pending_media = result
            continue

        if prompt.startswith("!"):
            if not config.enable_shell:
                print(_paint("Shell tools are disabled for this session.", "warning", use_color))
                continue
            command = prompt[1:].strip()
            if not command:
                continue
            prompt = (
                "Use the Agno coding shell tool to run this command if it is allowed by the configured "
                f"shell policy, then summarize the result:\n\n{command}"
            )

        try:
            media_kwargs = pending_media.to_agno_kwargs(config.resolved_workspace)
            team.print_response(
                prompt,
                stream=True,
                user_id=user_id,
                session_id=active_session_id,
                **media_kwargs,
            )
            if not pending_media.is_empty:
                pending_media = DeepAgentMedia()
        except RuntimeError as exc:
            print(_paint(f"Error: {exc}", "error", use_color), file=sys.stderr)
        except Exception as exc:  # pragma: no cover - keeps the REPL alive for provider errors.
            print(_paint(f"Unexpected error: {exc}", "error", use_color), file=sys.stderr)


def _handle_interactive_command(
    command: str,
    config: DeepAgentConfig,
    team: object,
    session_id: str,
    pending_media: DeepAgentMedia,
    use_color: bool,
) -> tuple[DeepAgentConfig, object, str, DeepAgentMedia] | None:
    name, _, rest = command.partition(" ")
    name = name.lower()
    rest = rest.strip()

    if name in {"/quit", "/exit", "/q"}:
        return None
    if name in {"/help", "/?"}:
        _print_interactive_help(use_color)
        return config, team, session_id, pending_media
    if name == "/status":
        _print_status(config, session_id, pending_media, use_color)
        return config, team, session_id, pending_media
    if name == "/clear":
        new_session_id = f"cli-{uuid4().hex[:8]}"
        print(_paint(f"New session: {new_session_id}", "accent", use_color))
        return config, create_deep_agent(config), new_session_id, DeepAgentMedia()
    if name == "/model":
        if not rest:
            print(_paint(f"Model: {config.model}", "accent", use_color))
            return config, team, session_id, pending_media
        new_config = replace(config, model=rest)
        print(_paint(f"Switched model to {rest}", "accent", use_color))
        return new_config, create_deep_agent(new_config), session_id, pending_media
    if name == "/compress":
        return _handle_compress_command(rest, config, team, session_id, pending_media, use_color)
    if name == "/attach":
        updated_media = _handle_attach_command(rest, pending_media, use_color)
        return config, team, session_id, updated_media
    if name in {"/media", "/attachments"}:
        print(_paint(_media_summary(pending_media), "accent", use_color))
        return config, team, session_id, pending_media

    print(_paint(f"Unknown command: {name}. Use /help.", "warning", use_color))
    return config, team, session_id, pending_media


def _handle_compress_command(
    rest: str,
    config: DeepAgentConfig,
    team: object,
    session_id: str,
    pending_media: DeepAgentMedia,
    use_color: bool,
) -> tuple[DeepAgentConfig, object, str, DeepAgentMedia]:
    value = rest.lower()
    if value in {"", "status"}:
        state = "on" if config.compress_tool_results else "off"
        print(_paint(f"Compression: {state}", "accent", use_color))
        return config, team, session_id, pending_media
    if value not in {"on", "off"}:
        print(_paint("Usage: /compress on | off | status", "warning", use_color))
        return config, team, session_id, pending_media

    new_config = replace(config, compress_tool_results=(value == "on"))
    print(_paint(f"Compression switched {value}", "accent", use_color))
    return new_config, create_deep_agent(new_config), session_id, pending_media


def _handle_attach_command(rest: str, pending_media: DeepAgentMedia, use_color: bool) -> DeepAgentMedia:
    media_type, _, source = rest.partition(" ")
    media_type = media_type.lower().strip()
    source = source.strip()
    if media_type not in {"image", "audio", "video", "file"} or not source:
        print(_paint("Usage: /attach image|audio|video|file <path-or-url>", "warning", use_color))
        return pending_media

    media = {
        "images": list(pending_media.images),
        "audio": list(pending_media.audio),
        "videos": list(pending_media.videos),
        "files": list(pending_media.files),
    }
    key = "images" if media_type == "image" else "videos" if media_type == "video" else media_type
    if media_type == "file":
        key = "files"
    media[key].append(source)
    updated = DeepAgentMedia(
        images=tuple(media["images"]),
        audio=tuple(media["audio"]),
        videos=tuple(media["videos"]),
        files=tuple(media["files"]),
    )
    print(_paint(f"Attached {media_type}: {source}", "accent", use_color))
    return updated


def _print_banner(
    config: DeepAgentConfig,
    session_id: str,
    pending_media: DeepAgentMedia,
    use_color: bool,
) -> None:
    title = _paint("Agno Deep Agent", "primary", use_color)
    print(f"{title} {_paint('interactive CLI', 'muted', use_color)}")
    print(
        _paint(
            f"model={config.model} session={session_id} compression={'on' if config.compress_tool_results else 'off'}",
            "muted",
            use_color,
        )
    )
    if not pending_media.is_empty:
        print(_paint(_media_summary(pending_media), "accent", use_color))
    print(_paint("Type /help for commands, /quit to exit.", "muted", use_color))


def _print_interactive_help(use_color: bool) -> None:
    print(_paint("Commands", "primary", use_color))
    print("  /status                     show model, workspace, compression, and pending media")
    print("  /model [provider:model]     show or switch model")
    print("  /compress on|off|status     toggle Agno tool-result compression")
    print("  /attach image <path|url>    attach image to the next prompt")
    print("  /attach audio <path|url>    attach audio to the next prompt")
    print("  /attach video <path|url>    attach video to the next prompt")
    print("  /attach file <path|url>     attach a document/file to the next prompt")
    print("  /media                      show pending attachments")
    print("  /clear                      start a fresh session id")
    print("  !<command>                  ask the agent to run an allowed shell command")
    print("  /quit                       exit")


def _print_status(
    config: DeepAgentConfig,
    session_id: str,
    pending_media: DeepAgentMedia,
    use_color: bool,
) -> None:
    shell_policy = "disabled"
    if config.enable_shell:
        shell_policy = "all" if config.allow_all_shell_commands else ",".join(config.allowed_shell_commands)
    lines = [
        f"Model: {config.model}",
        f"Workspace: {config.resolved_workspace}",
        f"Session: {session_id}",
        f"Skills: {config.resolved_skills_dir}",
        f"DB: {config.resolved_db_file}",
        f"Compression: {'on' if config.compress_tool_results else 'off'}",
        f"Media: {'send' if config.send_media_to_model else 'metadata-only'}, {'store' if config.store_media else 'do-not-store'}",
        f"Shell: {shell_policy}",
        _media_summary(pending_media),
    ]
    print(_paint("\n".join(lines), "accent", use_color))


def _media_summary(media: DeepAgentMedia) -> str:
    return (
        "Pending media: "
        f"{len(media.images)} image(s), "
        f"{len(media.audio)} audio item(s), "
        f"{len(media.videos)} video(s), "
        f"{len(media.files)} file(s)"
    )


def _use_color(args: argparse.Namespace) -> bool:
    return not getattr(args, "no_color", False) and sys.stdout.isatty() and os.getenv("NO_COLOR") is None


def _paint(text: str, style: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{AGNO_COLORS.get(style, '')}{text}{AGNO_COLORS['reset']}"


if __name__ == "__main__":
    raise SystemExit(main())
