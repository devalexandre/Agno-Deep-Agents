"""Factories for an Agno-based Deep Agent.

This module keeps the public surface intentionally small: configure, create,
and run. The depth comes from Agno primitives composed with strong defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Sequence, TypeVar

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.media import Audio, File, Image, Video
from agno.models.base import Model
from agno.models.utils import get_model
from agno.skills import LocalSkills, Skills
from agno.team import Team, TeamMode
from agno.tools.coding import CodingTools


DEFAULT_ALLOWED_SHELL_COMMANDS = (
    "python",
    "python3",
    "pytest",
    "pip",
    "pip3",
    "ruff",
    "mypy",
    "git",
    "ls",
    "find",
    "grep",
    "sed",
    "cat",
    "head",
    "tail",
    "wc",
    "pwd",
    "diff",
    "sort",
    "uniq",
    "mkdir",
    "touch",
)

DEFAULT_LOCAL_OLLAMA_HOST = "http://localhost:11434"

AGNO_COMPRESSION_PROMPT = """\
Compress this tool result for a coding deep-agent session.

Preserve:
- file paths, symbols, command names, errors, versions, ids, URLs, numbers, dates, and decisions
- test results, failing assertions, stack traces, and exact commands when useful
- user requirements and project constraints that affect the next action

Remove:
- repeated boilerplate, long unrelated logs, generic prose, and decorative formatting
- content that does not help the agent choose the next step

Return compact plain text. Prefer short sections named Facts, Evidence, Risks, and Next step when they fit.
"""

MediaItem = TypeVar("MediaItem", Image, Audio, Video, File)
ImageSource = str | Path | Image
AudioSource = str | Path | Audio
VideoSource = str | Path | Video
FileSource = str | Path | File


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", ""}


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc


@dataclass(slots=True)
class DeepAgentMedia:
    """Multimodal inputs that can be sent to an Agno Deep Agent run."""

    images: Sequence[ImageSource] = field(default_factory=tuple)
    audio: Sequence[AudioSource] = field(default_factory=tuple)
    videos: Sequence[VideoSource] = field(default_factory=tuple)
    files: Sequence[FileSource] = field(default_factory=tuple)

    @property
    def is_empty(self) -> bool:
        return not any((self.images, self.audio, self.videos, self.files))

    def to_agno_kwargs(self, workspace: Path | str) -> dict[str, Any]:
        """Return keyword arguments accepted by Agent/Team run methods."""

        return _build_media_kwargs(Path(workspace).expanduser().resolve(), media=self)


@dataclass(slots=True)
class DeepAgentConfig:
    """Configuration for the Agno Deep Agent harness."""

    workspace: Path | str = field(
        default_factory=lambda: Path(os.getenv("DEEP_AGENT_WORKSPACE", "."))
    )
    db_file: Path | str | None = None
    skills_dir: Path | str | None = None
    model: str | Model = field(
        default_factory=lambda: os.getenv("DEEP_AGENT_MODEL", "openai-responses:gpt-5.2")
    )
    tools: Sequence[Any] = field(default_factory=tuple)
    instructions: str | Sequence[str] | None = None
    ollama_host: str | None = field(default_factory=lambda: os.getenv("OLLAMA_HOST"))
    enable_shell: bool = True
    allowed_shell_commands: Iterable[str] = DEFAULT_ALLOWED_SHELL_COMMANDS
    allow_all_shell_commands: bool = False
    compress_tool_results: bool = field(
        default_factory=lambda: _env_bool("DEEP_AGENT_COMPRESS_TOOL_RESULTS", True)
    )
    compression_model: str | Model | None = field(
        default_factory=lambda: os.getenv("DEEP_AGENT_COMPRESSION_MODEL")
    )
    compression_tool_results_limit: int | None = field(
        default_factory=lambda: _env_int("DEEP_AGENT_COMPRESSION_LIMIT", 3)
    )
    compression_token_limit: int | None = field(
        default_factory=lambda: _env_int("DEEP_AGENT_COMPRESSION_TOKEN_LIMIT")
    )
    send_media_to_model: bool = field(default_factory=lambda: _env_bool("DEEP_AGENT_SEND_MEDIA", True))
    store_media: bool = True
    max_iterations: int = 8
    debug_mode: bool = False
    show_members_responses: bool = True

    @property
    def resolved_workspace(self) -> Path:
        return Path(self.workspace).expanduser().resolve()

    @property
    def resolved_db_file(self) -> Path:
        if self.db_file is not None:
            return Path(self.db_file).expanduser().resolve()
        return self.resolved_workspace / ".deep-agent" / "agno.db"

    @property
    def resolved_skills_dir(self) -> Path:
        if self.skills_dir is not None:
            return Path(self.skills_dir).expanduser().resolve()
        return self.resolved_workspace / "skills"


def create_deep_agent(
    config: DeepAgentConfig | None = None,
    *,
    model: str | Model | None = None,
    tools: Sequence[Any] | None = None,
    instructions: str | Sequence[str] | None = None,
    workspace: Path | str | None = None,
    db_file: Path | str | None = None,
    skills_dir: Path | str | None = None,
    ollama_host: str | None = None,
    enable_shell: bool | None = None,
    allowed_shell_commands: Iterable[str] | None = None,
    allow_all_shell_commands: bool | None = None,
    compress_tool_results: bool | None = None,
    compression_model: str | Model | None = None,
    compression_tool_results_limit: int | None = None,
    compression_token_limit: int | None = None,
    send_media_to_model: bool | None = None,
    store_media: bool | None = None,
    max_iterations: int | None = None,
    debug_mode: bool | None = None,
    show_members_responses: bool | None = None,
) -> Team:
    """Create a task-oriented Deep Agent team using Agno primitives."""

    resolved_config = config or DeepAgentConfig()
    overrides: dict[str, Any] = {}
    if model is not None:
        overrides["model"] = model
    if tools is not None:
        overrides["tools"] = tools
    if instructions is not None:
        overrides["instructions"] = instructions
    if workspace is not None:
        overrides["workspace"] = workspace
    if db_file is not None:
        overrides["db_file"] = db_file
    if skills_dir is not None:
        overrides["skills_dir"] = skills_dir
    if ollama_host is not None:
        overrides["ollama_host"] = ollama_host
    if enable_shell is not None:
        overrides["enable_shell"] = enable_shell
    if allowed_shell_commands is not None:
        overrides["allowed_shell_commands"] = allowed_shell_commands
    if allow_all_shell_commands is not None:
        overrides["allow_all_shell_commands"] = allow_all_shell_commands
    if compress_tool_results is not None:
        overrides["compress_tool_results"] = compress_tool_results
    if compression_model is not None:
        overrides["compression_model"] = compression_model
    if compression_tool_results_limit is not None:
        overrides["compression_tool_results_limit"] = compression_tool_results_limit
    if compression_token_limit is not None:
        overrides["compression_token_limit"] = compression_token_limit
    if send_media_to_model is not None:
        overrides["send_media_to_model"] = send_media_to_model
    if store_media is not None:
        overrides["store_media"] = store_media
    if max_iterations is not None:
        overrides["max_iterations"] = max_iterations
    if debug_mode is not None:
        overrides["debug_mode"] = debug_mode
    if show_members_responses is not None:
        overrides["show_members_responses"] = show_members_responses
    if overrides:
        resolved_config = replace(resolved_config, **overrides)

    workspace = resolved_config.resolved_workspace
    workspace.mkdir(parents=True, exist_ok=True)
    resolved_config.resolved_db_file.parent.mkdir(parents=True, exist_ok=True)

    db = SqliteDb(db_file=str(resolved_config.resolved_db_file))
    skills = _load_skills(resolved_config.resolved_skills_dir)

    researcher = Agent(
        id="deep-agent-researcher",
        name="Researcher",
        role=(
            "Map requirements, inspect the workspace, identify constraints, "
            "and explain implementation risks before code changes."
        ),
        model=_build_model(resolved_config),
        tools=[_read_only_workspace_tools(workspace)],
        db=db,
        learning=True,
        enable_agentic_memory=True,
        add_history_to_context=True,
        add_datetime_to_context=True,
        compress_tool_results=resolved_config.compress_tool_results,
        compression_manager=_build_compression_manager(resolved_config),
        send_media_to_model=resolved_config.send_media_to_model,
        store_media=resolved_config.store_media,
        markdown=True,
        instructions=[
            "Your job is discovery only unless explicitly asked otherwise.",
            "Start by identifying the relevant files, commands, docs, and constraints.",
            "Use direct evidence: paths, symbols, nearby tests, config files, tool output, and user-provided media.",
            "Prefer a small number of high-value reads/searches over broad scanning.",
            "Return concise findings with: evidence, risks, likely files to edit, and suggested next step.",
        ],
    )

    implementer = Agent(
        id="deep-agent-implementer",
        name="Implementer",
        role=(
            "Make scoped workspace changes, create files when needed, and run "
            "allowed verification commands."
        ),
        model=_build_model(resolved_config),
        tools=[_coding_workspace_tools(resolved_config)],
        db=db,
        learning=True,
        enable_agentic_memory=True,
        add_history_to_context=True,
        add_datetime_to_context=True,
        compress_tool_results=resolved_config.compress_tool_results,
        compression_manager=_build_compression_manager(resolved_config),
        send_media_to_model=resolved_config.send_media_to_model,
        store_media=resolved_config.store_media,
        markdown=True,
        instructions=[
            "Read the current file contents before editing.",
            "Make the smallest complete change that satisfies the user's requested outcome.",
            "Preserve existing public behavior unless the user asks to change it.",
            "Use existing project conventions for names, style, dependencies, and tests.",
            "Prefer exact, incremental edits. Avoid broad rewrites and unrelated cleanup.",
            "Run targeted checks when shell execution is available; otherwise inspect enough code to explain the verification gap.",
        ],
    )

    reviewer = Agent(
        id="deep-agent-reviewer",
        name="Reviewer",
        role=(
            "Review the produced work for correctness, missing tests, regressions, "
            "and user-facing clarity."
        ),
        model=_build_model(resolved_config),
        tools=[_review_workspace_tools(resolved_config)],
        db=db,
        learning=True,
        enable_agentic_memory=True,
        add_history_to_context=True,
        add_datetime_to_context=True,
        compress_tool_results=resolved_config.compress_tool_results,
        compression_manager=_build_compression_manager(resolved_config),
        send_media_to_model=resolved_config.send_media_to_model,
        store_media=resolved_config.store_media,
        markdown=True,
        instructions=[
            "Review the final work as if it will be shipped.",
            "Prioritize correctness bugs, behavioral regressions, missing tests, security assumptions, and confusing user-facing behavior.",
            "Check whether the implementation matches the user's exact request and visible project conventions.",
            "Call out residual risk plainly and suggest the smallest useful follow-up only when needed.",
        ],
    )

    team = Team(
        id="agno-deep-agent",
        name="Agno Deep Agent",
        model=_build_model(resolved_config),
        members=[researcher, implementer, reviewer],
        mode=TeamMode.tasks,
        max_iterations=resolved_config.max_iterations,
        skills=skills,
        tools=[_leader_workspace_tools(workspace), *resolved_config.tools],
        db=db,
        learning=True,
        enable_agentic_memory=True,
        enable_session_summaries=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_datetime_to_context=True,
        send_media_to_model=resolved_config.send_media_to_model,
        store_media=resolved_config.store_media,
        markdown=True,
        show_members_responses=resolved_config.show_members_responses,
        debug_mode=resolved_config.debug_mode,
        compress_tool_results=resolved_config.compress_tool_results,
        compression_manager=_build_compression_manager(resolved_config),
        instructions=[
            "You are an Agno-based Deep Agent harness for long-running tasks.",
            "Always restate the concrete goal internally as: outcome, constraints, files or media involved, verification.",
            "For complex work, create a compact task list: discover, implement, verify, report.",
            "Delegate discovery, implementation, and review to the specialist members when their tools or focus help.",
            "For simple work, keep the loop short and avoid unnecessary delegation.",
            "Use skills progressively: inspect summaries first, load full instructions only when the skill clearly applies.",
            "Use workspace tools only inside the configured workspace.",
            "Treat shell execution as workspace-restricted command execution, not a full security sandbox.",
            "When media is attached, pass the relevant image, audio, video, or file context to the member best suited for the task.",
            "When compression is enabled, trust compressed tool results as summaries and re-read original files only when exact text matters.",
            "Small-model rule: be literal, use short steps, avoid hidden assumptions, and ask for clarification only when proceeding would be risky.",
            "Persist useful user preferences, project facts, decisions, and task context when they matter later.",
            "Finish in the user's language with: what changed, what was verified, and any remaining risk.",
            *_normalize_instructions(resolved_config.instructions),
        ],
    )
    return team


def run_deep_agent(
    task: str,
    config: DeepAgentConfig | None = None,
    *,
    stream: bool = True,
    user_id: str | None = None,
    session_id: str | None = None,
    media: DeepAgentMedia | None = None,
    images: Sequence[ImageSource] | None = None,
    audio: Sequence[AudioSource] | None = None,
    videos: Sequence[VideoSource] | None = None,
    files: Sequence[FileSource] | None = None,
) -> None:
    """Create the harness and print a response for a single task."""

    resolved_config = config or DeepAgentConfig()
    team = create_deep_agent(resolved_config)
    media_kwargs = _build_media_kwargs(
        resolved_config.resolved_workspace,
        media=media,
        images=images,
        audio=audio,
        videos=videos,
        files=files,
    )
    team.print_response(
        task,
        stream=stream,
        user_id=user_id,
        session_id=session_id,
        **media_kwargs,
    )


def _build_model(config: DeepAgentConfig) -> Model:
    model = config.model
    if isinstance(model, Model):
        return model
    if not isinstance(model, str) or not model.strip():
        raise RuntimeError("Model must be a non-empty provider string or an Agno Model instance.")

    model_spec = model.strip()
    if ":" not in model_spec:
        return _build_openai_responses_model(model_spec)

    provider, model_id = model_spec.split(":", 1)
    provider = provider.strip().lower()
    model_id = model_id.strip()
    if not provider or not model_id:
        raise RuntimeError("Model strings must use '<provider>:<model-id>', for example 'ollama:devstral-2'.")

    try:
        if provider in {"openai-responses", "responses"}:
            return _build_openai_responses_model(model_id)
        if provider == "ollama":
            from agno.models.ollama import Ollama

            return Ollama(id=model_id, host=config.ollama_host or DEFAULT_LOCAL_OLLAMA_HOST)
        if provider in {"ollama-responses", "ollama-openai-responses"}:
            from agno.models.ollama import OllamaResponses

            return OllamaResponses(id=model_id, host=config.ollama_host or DEFAULT_LOCAL_OLLAMA_HOST)
        if provider == "ollama-cloud":
            from agno.models.ollama import Ollama

            return Ollama(id=model_id, host=config.ollama_host)
        if provider in {"ollama-cloud-responses", "ollama-cloud-openai-responses"}:
            from agno.models.ollama import OllamaResponses

            return OllamaResponses(id=model_id, host=config.ollama_host)
        return get_model(model_spec)
    except ImportError as exc:
        package = "ollama" if provider.startswith("ollama") else provider
        raise RuntimeError(
            f"The '{provider}' model backend is not installed. Run `pip install {package}` "
            "or `pip install -r requirements.txt` inside this project environment."
        ) from exc


def _build_openai_responses_model(model_id: str) -> Model:
    try:
        from agno.models.openai import OpenAIResponses
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI model backend is not installed. Run `pip install -r requirements.txt` "
            "inside this project environment."
        ) from exc

    return OpenAIResponses(id=model_id)


def _build_compression_manager(config: DeepAgentConfig) -> Any:
    if not config.compress_tool_results:
        return None

    from agno.compression.manager import CompressionManager

    model: Model | None = None
    if config.compression_model is not None:
        if isinstance(config.compression_model, Model):
            model = config.compression_model
        else:
            model = _build_model(replace(config, model=config.compression_model))

    return CompressionManager(
        model=model,
        compress_tool_results=True,
        compress_tool_results_limit=config.compression_tool_results_limit,
        compress_token_limit=config.compression_token_limit,
        compress_tool_call_instructions=AGNO_COMPRESSION_PROMPT,
    )


def _normalize_instructions(instructions: str | Sequence[str] | None) -> list[str]:
    if instructions is None:
        return []
    if isinstance(instructions, str):
        return [instructions]
    return list(instructions)


def _load_skills(skills_dir: Path) -> Skills | None:
    if not skills_dir.exists():
        return None
    return Skills(loaders=[LocalSkills(str(skills_dir))])


def _build_media_kwargs(
    workspace: Path,
    *,
    media: DeepAgentMedia | None = None,
    images: Sequence[ImageSource] | None = None,
    audio: Sequence[AudioSource] | None = None,
    videos: Sequence[VideoSource] | None = None,
    files: Sequence[FileSource] | None = None,
) -> dict[str, Any]:
    merged = DeepAgentMedia(
        images=tuple(media.images if media else ()) + tuple(images or ()),
        audio=tuple(media.audio if media else ()) + tuple(audio or ()),
        videos=tuple(media.videos if media else ()) + tuple(videos or ()),
        files=tuple(media.files if media else ()) + tuple(files or ()),
    )
    if merged.is_empty:
        return {}

    return {
        "images": _normalize_media_sources(Image, merged.images, workspace),
        "audio": _normalize_media_sources(Audio, merged.audio, workspace),
        "videos": _normalize_media_sources(Video, merged.videos, workspace),
        "files": _normalize_media_sources(File, merged.files, workspace),
    }


def _normalize_media_sources(
    media_type: type[MediaItem],
    sources: Sequence[str | Path | MediaItem],
    workspace: Path,
) -> list[MediaItem] | None:
    if not sources:
        return None

    normalized: list[MediaItem] = []
    for source in sources:
        if isinstance(source, media_type):
            normalized.append(source)
            continue

        source_text = str(source)
        kwargs: dict[str, Any]
        if source_text.startswith(("http://", "https://")):
            kwargs = {"url": source_text}
        else:
            path = Path(source).expanduser()
            if not path.is_absolute():
                path = workspace / path
            kwargs = {"filepath": path}

        suffix = _media_format(source_text)
        if suffix:
            kwargs["format"] = suffix
        normalized.append(media_type(**kwargs))

    return normalized


def _media_format(source: str) -> str | None:
    suffix = Path(source.split("?", 1)[0]).suffix.lower().lstrip(".")
    return suffix or None


def _leader_workspace_tools(workspace: Path) -> CodingTools:
    return CodingTools(
        base_dir=workspace,
        restrict_to_base_dir=True,
        enable_read_file=True,
        enable_edit_file=False,
        enable_write_file=False,
        enable_run_shell=False,
        enable_grep=True,
        enable_find=True,
        enable_ls=True,
    )


def _read_only_workspace_tools(workspace: Path) -> CodingTools:
    return CodingTools(
        base_dir=workspace,
        restrict_to_base_dir=True,
        enable_read_file=True,
        enable_edit_file=False,
        enable_write_file=False,
        enable_run_shell=False,
        enable_grep=True,
        enable_find=True,
        enable_ls=True,
    )


def _coding_workspace_tools(config: DeepAgentConfig) -> CodingTools:
    tools = CodingTools(
        base_dir=config.resolved_workspace,
        restrict_to_base_dir=True,
        enable_read_file=True,
        enable_edit_file=True,
        enable_write_file=True,
        enable_run_shell=config.enable_shell,
        enable_grep=True,
        enable_find=True,
        enable_ls=True,
        allowed_commands=list(config.allowed_shell_commands),
        shell_timeout=120,
    )
    if config.allow_all_shell_commands:
        tools.allowed_commands = None
    return tools


def _review_workspace_tools(config: DeepAgentConfig) -> CodingTools:
    tools = CodingTools(
        base_dir=config.resolved_workspace,
        restrict_to_base_dir=True,
        enable_read_file=True,
        enable_edit_file=False,
        enable_write_file=False,
        enable_run_shell=config.enable_shell,
        enable_grep=True,
        enable_find=True,
        enable_ls=True,
        allowed_commands=list(config.allowed_shell_commands),
        shell_timeout=120,
    )
    if config.allow_all_shell_commands:
        tools.allowed_commands = None
    return tools
