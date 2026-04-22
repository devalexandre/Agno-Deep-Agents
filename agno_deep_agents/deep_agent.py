"""Factories for an Agno-based Deep Agent.

This module keeps the public surface intentionally small: configure, create,
and run. The depth comes from Agno primitives composed with strong defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
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
        markdown=True,
        instructions=[
            "Gather concrete context before making recommendations.",
            "Prefer file and symbol evidence over assumptions.",
            "Return concise findings with paths, risks, and suggested next steps.",
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
        markdown=True,
        instructions=[
            "Read existing files before editing them.",
            "Keep changes narrowly focused on the user's requested outcome.",
            "Use exact, incremental edits when possible.",
            "Run targeted checks when the shell is available.",
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
        markdown=True,
        instructions=[
            "Prioritize bugs, behavioral regressions, and missing verification.",
            "Call out residual risk plainly.",
            "Suggest the smallest useful follow-up when something remains open.",
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
        markdown=True,
        show_members_responses=resolved_config.show_members_responses,
        debug_mode=resolved_config.debug_mode,
        instructions=[
            "You are an Agno-based Deep Agent harness for long-running tasks.",
            "Start by turning the user's goal into a compact task list.",
            "Delegate discovery, implementation, and review to the specialist members.",
            "Use skills progressively: inspect summaries first, load full instructions only when relevant.",
            "Use workspace tools only inside the configured workspace.",
            "Treat shell execution as workspace-restricted command execution, not a full security sandbox.",
            "Persist useful user preferences, project facts, decisions, and task context when they matter later.",
            "Finish with a concise response in the user's language, including changed files and verification.",
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
) -> None:
    """Create the harness and print a response for a single task."""

    team = create_deep_agent(config)
    team.print_response(task, stream=stream, user_id=user_id, session_id=session_id)


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
    return CodingTools(
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


def _review_workspace_tools(config: DeepAgentConfig) -> CodingTools:
    return CodingTools(
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
