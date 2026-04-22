from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from agno_deep_agents import DeepAgentConfig, run_deep_agent
from agno_deep_agents.acp_server import run_acp_server


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "acp":
        return _parse_acp_args(argv[1:])
    return _parse_run_args(argv)


def _parse_run_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agno-deep-agent",
        description="Run an opinionated Deep Agent built with Agno primitives.",
    )
    parser.set_defaults(command="run")
    parser.add_argument(
        "task",
        nargs="*",
        help="Task to run. If omitted, the task is read from stdin.",
    )
    _add_common_options(parser, include_session_id=True)
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Print the final response after completion instead of streaming.",
    )
    parser.add_argument(
        "--hide-members",
        action="store_true",
        help="Hide specialist member responses in the console output.",
    )
    return parser.parse_args(argv)


def _parse_acp_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agno-deep-agent acp",
        description="Run Agno Deep Agent as an ACP stdio server for editors and IDEs.",
    )
    parser.set_defaults(command="acp", no_stream=True, hide_members=True)
    _add_common_options(parser, include_session_id=False)
    return parser.parse_args(argv)


def _add_common_options(parser: argparse.ArgumentParser, *, include_session_id: bool) -> None:
    parser.add_argument(
        "--workspace",
        default=os.getenv("DEEP_AGENT_WORKSPACE", "."),
        help="Workspace root for file and shell tools.",
    )
    parser.add_argument(
        "--db-file",
        default=None,
        help="SQLite database path for sessions, memory, and learning.",
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="Directory containing Agno skills. Defaults to ./skills.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("DEEP_AGENT_MODEL", "openai-responses:gpt-5.2"),
        help="Model spec, for example openai-responses:gpt-5.2 or ollama:devstral-2.",
    )
    parser.add_argument(
        "--ollama-host",
        default=os.getenv("OLLAMA_HOST"),
        help="Optional Ollama host, for example http://localhost:11434.",
    )
    parser.add_argument(
        "--user-id",
        default=os.getenv("DEEP_AGENT_USER_ID"),
        help="Stable user id for memory.",
    )
    if include_session_id:
        parser.add_argument(
            "--session-id",
            default=os.getenv("DEEP_AGENT_SESSION_ID"),
            help="Stable session id for continuing a task.",
        )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=int(os.getenv("DEEP_AGENT_MAX_ITERATIONS", "8")),
        help="Maximum task-loop iterations for the team.",
    )
    parser.add_argument(
        "--no-shell",
        action="store_true",
        help="Disable shell execution while keeping filesystem tools enabled.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Agno debug mode.",
    )


def main() -> int:
    args = parse_args()
    uses_openai = ":" not in args.model or args.model.startswith(("openai:", "openai-responses:", "responses:"))
    if uses_openai and not os.getenv("OPENAI_API_KEY"):
        print(
            "Warning: OPENAI_API_KEY is not set; the run will fail when the model is called.",
            file=sys.stderr,
        )

    config = DeepAgentConfig(
        workspace=Path(args.workspace),
        db_file=Path(args.db_file) if args.db_file else None,
        skills_dir=Path(args.skills_dir) if args.skills_dir else None,
        model=args.model,
        ollama_host=args.ollama_host,
        enable_shell=not args.no_shell,
        max_iterations=args.max_iterations,
        debug_mode=args.debug,
        show_members_responses=not args.hide_members,
    )

    if args.command == "acp":
        return run_acp_server(config, user_id=args.user_id)

    task = " ".join(args.task).strip()
    if not task and not sys.stdin.isatty():
        task = sys.stdin.read().strip()
    if not task:
        print("Provide a task as an argument or through stdin.", file=sys.stderr)
        return 2

    try:
        run_deep_agent(
            task,
            config,
            stream=not args.no_stream,
            user_id=args.user_id,
            session_id=args.session_id,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
