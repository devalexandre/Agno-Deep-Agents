"""ACP stdio adapter for Agno Deep Agent.

The Agent Client Protocol uses newline-delimited JSON-RPC over stdout/stdin.
This module intentionally has no optional protocol dependency so the default
CLI install stays small and predictable.
"""

from __future__ import annotations

import json
import sys
import threading
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, TextIO
from uuid import uuid4

from agno.db.base import SessionType
from agno.db.sqlite import SqliteDb

from agno_deep_agents.deep_agent import DeepAgentConfig, create_deep_agent


ACP_PROTOCOL_VERSION = 1
JSONRPC_VERSION = "2.0"


class JsonRpcError(Exception):
    """JSON-RPC error that can be serialized back to the client."""

    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        error = {"code": self.code, "message": self.message}
        if self.data is not None:
            error["data"] = self.data
        return error


@dataclass(slots=True)
class ACPSession:
    """Runtime state for an ACP session."""

    session_id: str
    cwd: Path
    mcp_servers: list[dict[str, Any]] = field(default_factory=list)
    title: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    team: Any | None = None
    active_run_id: str | None = None
    active_request_id: Any | None = None
    cancel_requested: bool = False


class ACPServer:
    """Small JSON-RPC server that exposes Agno Deep Agent over ACP stdio."""

    def __init__(
        self,
        config: DeepAgentConfig,
        *,
        user_id: str | None = None,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
        log_stream: TextIO | None = None,
    ) -> None:
        self.config = config
        self.user_id = user_id
        self.input = input_stream or sys.stdin
        self.output = output_stream or sys.stdout
        self.log = log_stream or sys.stderr
        self.sessions: dict[str, ACPSession] = {}
        self._send_lock = threading.Lock()
        self._threads: list[threading.Thread] = []
        self._should_stop = False

    def serve_forever(self) -> int:
        """Read JSON-RPC messages from stdin until EOF or exit notification."""

        for raw_line in self.input:
            if self._should_stop:
                break
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                message = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                self._send_error(None, JsonRpcError(-32700, "Parse error", str(exc)))
                continue

            try:
                self._handle_message(message)
            except JsonRpcError as exc:
                self._send_error(message.get("id"), exc)
            except Exception as exc:  # pragma: no cover - defensive protocol guard
                self._log_exception(exc)
                self._send_error(message.get("id"), JsonRpcError(-32603, "Internal error", str(exc)))

        self._cancel_active_runs()
        for thread in self._threads:
            thread.join(timeout=2)
        return 0

    def _handle_message(self, message: Any) -> None:
        if not isinstance(message, dict):
            raise JsonRpcError(-32600, "Invalid Request", "Message must be a JSON object.")
        if message.get("jsonrpc") != JSONRPC_VERSION:
            raise JsonRpcError(-32600, "Invalid Request", "jsonrpc must be '2.0'.")

        method = message.get("method")
        request_id = message.get("id")
        if not isinstance(method, str):
            raise JsonRpcError(-32600, "Invalid Request", "method is required.")

        params = message.get("params") or {}
        if not isinstance(params, dict):
            raise JsonRpcError(-32602, "Invalid params", "params must be an object when provided.")

        if method == "session/prompt":
            if request_id is None:
                raise JsonRpcError(-32600, "Invalid Request", "session/prompt must include an id.")
            self._start_prompt_thread(request_id, params)
            return

        result = self._dispatch(method, params)
        if request_id is not None:
            self._send_result(request_id, result)

    def _dispatch(self, method: str, params: dict[str, Any]) -> Any:
        if method == "initialize":
            return self._initialize(params)
        if method == "session/new":
            return self._session_new(params)
        if method == "session/load":
            return self._session_load(params)
        if method == "session/cancel":
            return self._session_cancel(params)
        if method == "shutdown":
            self._should_stop = True
            return None
        if method == "exit":
            self._should_stop = True
            return None
        raise JsonRpcError(-32601, "Method not found", method)

    def _initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        requested_version = params.get("protocolVersion", ACP_PROTOCOL_VERSION)
        protocol_version = ACP_PROTOCOL_VERSION if requested_version != ACP_PROTOCOL_VERSION else requested_version
        return {
            "protocolVersion": protocol_version,
            "agentCapabilities": {
                "loadSession": True,
                "promptCapabilities": {
                    "image": False,
                    "audio": False,
                    "embeddedContext": True,
                },
                "mcpCapabilities": {
                    "http": False,
                    "sse": False,
                },
            },
            "agentInfo": {
                "name": "agno-deep-agent",
                "title": "Agno Deep Agent",
                "version": _package_version(),
            },
            "authMethods": [],
        }

    def _session_new(self, params: dict[str, Any]) -> dict[str, str]:
        cwd = self._resolve_cwd(params)
        session_id = f"agdeep_{uuid4().hex}"
        self.sessions[session_id] = ACPSession(
            session_id=session_id,
            cwd=cwd,
            mcp_servers=list(params.get("mcpServers") or []),
        )
        return {"sessionId": session_id}

    def _session_load(self, params: dict[str, Any]) -> None:
        session_id = params.get("sessionId")
        if not isinstance(session_id, str) or not session_id:
            raise JsonRpcError(-32602, "Invalid params", "sessionId is required.")

        cwd = self._resolve_cwd(params)
        session = ACPSession(
            session_id=session_id,
            cwd=cwd,
            mcp_servers=list(params.get("mcpServers") or []),
        )
        self.sessions[session_id] = session
        self._replay_session(session)
        return None

    def _session_cancel(self, params: dict[str, Any]) -> None:
        session_id = params.get("sessionId")
        session = self._get_session(session_id)
        session.cancel_requested = True
        if session.team is not None and session.active_run_id:
            try:
                session.team.cancel_run(session.active_run_id)
            except Exception as exc:  # pragma: no cover - best effort cancellation
                self._log(f"Unable to cancel run {session.active_run_id}: {exc}")
        return None

    def _start_prompt_thread(self, request_id: Any, params: dict[str, Any]) -> None:
        session = self._get_session(params.get("sessionId"))
        if session.active_request_id is not None:
            raise JsonRpcError(-32000, "Session is already running a prompt turn.")
        session.active_request_id = request_id
        session.cancel_requested = False

        thread = threading.Thread(
            target=self._run_prompt_thread,
            args=(request_id, params),
            name=f"agdeep-acp-{session.session_id}",
            daemon=True,
        )
        self._threads.append(thread)
        thread.start()

    def _run_prompt_thread(self, request_id: Any, params: dict[str, Any]) -> None:
        session_id = params.get("sessionId")
        try:
            result = self._session_prompt(params)
            self._send_result(request_id, result)
        except JsonRpcError as exc:
            self._send_error(request_id, exc)
        except Exception as exc:
            self._log_exception(exc)
            self._send_error(request_id, JsonRpcError(-32000, "Prompt turn failed", str(exc)))
        finally:
            try:
                session = self._get_session(session_id)
            except JsonRpcError:
                session = None
            if session is not None:
                session.active_request_id = None
                session.active_run_id = None

    def _session_prompt(self, params: dict[str, Any]) -> dict[str, str]:
        session = self._get_session(params.get("sessionId"))
        prompt = params.get("prompt")
        task = _content_blocks_to_markdown(prompt)
        if not task.strip():
            raise JsonRpcError(-32602, "Invalid params", "prompt must contain text or resource content.")

        session.title = session.title or _title_from_task(task)
        session.updated_at = datetime.now(UTC)
        self._send_session_info(session)
        self._send_plan(
            session.session_id,
            [
                ("Read the editor prompt and attached context", "high", "completed"),
                ("Run the Agno Deep Agent team", "high", "in_progress"),
                ("Return the final response to the ACP client", "medium", "pending"),
            ],
        )

        final_output: Any | None = None
        sent_content = False

        with redirect_stdout(self.log):
            team = self._team_for_session(session)
            stream = team.run(
                task,
                stream=True,
                stream_events=True,
                session_id=session.session_id,
                user_id=self.user_id,
                metadata={
                    "acp": {
                        "cwd": str(session.cwd),
                        "session_id": session.session_id,
                    }
                },
                yield_run_output=True,
            )
            for event in stream:
                if session.cancel_requested:
                    return {"stopReason": "cancelled"}
                run_id = getattr(event, "run_id", None)
                if run_id:
                    session.active_run_id = run_id
                if _is_team_run_output(event):
                    final_output = event
                    continue
                sent_content = self._handle_agno_event(session, event) or sent_content

        if session.cancel_requested:
            return {"stopReason": "cancelled"}

        final_text = _output_to_text(final_output)
        if final_text and not sent_content:
            self._send_agent_message(session.session_id, final_text)

        self._send_plan(
            session.session_id,
            [
                ("Read the editor prompt and attached context", "high", "completed"),
                ("Run the Agno Deep Agent team", "high", "completed"),
                ("Return the final response to the ACP client", "medium", "completed"),
            ],
        )
        session.updated_at = datetime.now(UTC)
        self._send_session_info(session)
        return {"stopReason": "end_turn"}

    def _handle_agno_event(self, session: ACPSession, event: Any) -> bool:
        event_name = getattr(event, "event", "") or event.__class__.__name__
        content = getattr(event, "content", None)

        if "TaskStateUpdated" in event.__class__.__name__ or event_name.endswith("TaskStateUpdated"):
            entries = _plan_entries_from_tasks(getattr(event, "tasks", None))
            if entries:
                self._send_update(session.session_id, {"sessionUpdate": "plan", "entries": entries})
            return False

        if "TaskCreated" in event.__class__.__name__ or event_name.endswith("TaskCreated"):
            entry = _plan_entry_from_event(event)
            if entry:
                self._send_update(session.session_id, {"sessionUpdate": "plan", "entries": [entry]})
            return False

        if "ToolCallStarted" in event.__class__.__name__ or event_name.endswith("ToolCallStarted"):
            tool = getattr(event, "tool", None)
            self._send_tool_call(session.session_id, tool, "in_progress")
            return False

        if "ToolCallCompleted" in event.__class__.__name__ or event_name.endswith("ToolCallCompleted"):
            tool = getattr(event, "tool", None)
            self._send_tool_call_update(session.session_id, tool, "completed", content)
            return False

        if "ToolCallError" in event.__class__.__name__ or event_name.endswith("ToolCallError"):
            tool = getattr(event, "tool", None)
            self._send_tool_call_update(session.session_id, tool, "failed", content)
            return False

        if content and (
            "RunContent" in event.__class__.__name__
            or event_name.endswith("RunContent")
            or "IntermediateRunContent" in event.__class__.__name__
        ):
            text = _stringify_content(content)
            if text:
                self._send_agent_message(session.session_id, text)
                return True

        return False

    def _team_for_session(self, session: ACPSession) -> Any:
        if session.team is None:
            session_config = replace(
                self.config,
                workspace=session.cwd,
                show_members_responses=False,
            )
            session.team = create_deep_agent(session_config)
        return session.team

    def _replay_session(self, session: ACPSession) -> None:
        db = SqliteDb(db_file=str(self._db_file_for_session(session)))
        stored = db.get_session(session.session_id, SessionType.TEAM, user_id=self.user_id)
        if stored is None:
            return

        runs = getattr(stored, "runs", None) or []
        for run in runs:
            user_text = _run_input_to_text(run)
            if user_text:
                self._send_update(
                    session.session_id,
                    {"sessionUpdate": "user_message_chunk", "content": {"type": "text", "text": user_text}},
                )
            agent_text = _output_to_text(run)
            if agent_text:
                self._send_agent_message(session.session_id, agent_text)

        updated_at = getattr(stored, "updated_at", None)
        if isinstance(updated_at, int):
            session.updated_at = datetime.fromtimestamp(updated_at, UTC)
        self._send_session_info(session)

    def _db_file_for_session(self, session: ACPSession) -> Path:
        if self.config.db_file is not None:
            return Path(self.config.db_file).expanduser().resolve()
        return session.cwd / ".deep-agent" / "agno.db"

    def _resolve_cwd(self, params: dict[str, Any]) -> Path:
        cwd = params.get("cwd") or str(self.config.resolved_workspace)
        if not isinstance(cwd, str) or not cwd:
            raise JsonRpcError(-32602, "Invalid params", "cwd must be a non-empty string.")
        candidate = Path(cwd).expanduser()
        if candidate.is_absolute():
            return candidate.resolve()

        # Some ACP clients send relative cwd values such as "." during
        # handshake/session creation. Resolve those relative paths against the
        # server workspace to improve compatibility across editor plugins.
        return (self.config.resolved_workspace / candidate).resolve()

    def _get_session(self, session_id: Any) -> ACPSession:
        if not isinstance(session_id, str) or not session_id:
            raise JsonRpcError(-32602, "Invalid params", "sessionId is required.")
        session = self.sessions.get(session_id)
        if session is None:
            raise JsonRpcError(-32001, "Unknown session", session_id)
        return session

    def _send_plan(self, session_id: str, entries: list[tuple[str, str, str]]) -> None:
        self._send_update(
            session_id,
            {
                "sessionUpdate": "plan",
                "entries": [
                    {"content": content, "priority": priority, "status": status}
                    for content, priority, status in entries
                ],
            },
        )

    def _send_session_info(self, session: ACPSession) -> None:
        self._send_update(
            session.session_id,
            {
                "sessionUpdate": "session_info_update",
                "title": session.title,
                "updatedAt": session.updated_at.isoformat().replace("+00:00", "Z"),
                "_meta": {
                    "cwd": str(session.cwd),
                    "model": str(self.config.model),
                },
            },
        )

    def _send_agent_message(self, session_id: str, text: str) -> None:
        self._send_update(
            session_id,
            {"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": text}},
        )

    def _send_tool_call(self, session_id: str, tool: Any, status: str) -> None:
        self._send_update(
            session_id,
            {
                "sessionUpdate": "tool_call",
                "toolCallId": _tool_call_id(tool),
                "title": _tool_title(tool),
                "kind": "other",
                "status": status,
                "rawInput": _tool_input(tool),
            },
        )

    def _send_tool_call_update(self, session_id: str, tool: Any, status: str, content: Any) -> None:
        update: dict[str, Any] = {
            "sessionUpdate": "tool_call_update",
            "toolCallId": _tool_call_id(tool),
            "status": _normalize_tool_status(status),
            "title": _tool_title(tool),
            "rawOutput": _tool_output(tool),
        }
        text = _stringify_content(content)
        if text:
            update["content"] = [{"type": "content", "content": {"type": "text", "text": text}}]
        self._send_update(session_id, update)

    def _send_update(self, session_id: str, update: dict[str, Any]) -> None:
        self._send_notification(
            "session/update",
            {
                "sessionId": session_id,
                "update": update,
            },
        )

    def _send_result(self, request_id: Any, result: Any) -> None:
        self._send({"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result})

    def _send_error(self, request_id: Any, error: JsonRpcError) -> None:
        self._send({"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error.to_dict()})

    def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        self._send({"jsonrpc": JSONRPC_VERSION, "method": method, "params": params})

    def _send(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with self._send_lock:
            self.output.write(line)
            self.output.write("\n")
            self.output.flush()

    def _cancel_active_runs(self) -> None:
        for session in self.sessions.values():
            if session.active_request_id is not None:
                session.cancel_requested = True
                if session.team is not None and session.active_run_id:
                    try:
                        session.team.cancel_run(session.active_run_id)
                    except Exception:
                        pass

    def _log(self, message: str) -> None:
        print(message, file=self.log)

    def _log_exception(self, exc: BaseException) -> None:
        print(f"ACP server error: {exc}", file=self.log)
        traceback.print_exc(file=self.log)


def run_acp_server(config: DeepAgentConfig, *, user_id: str | None = None) -> int:
    """Run the ACP stdio server."""

    return ACPServer(config, user_id=user_id).serve_forever()


def _package_version() -> str:
    try:
        return version("agno-deep-agent")
    except PackageNotFoundError:
        return "0.0.0"


def _content_blocks_to_markdown(prompt: Any) -> str:
    if isinstance(prompt, str):
        return prompt
    if isinstance(prompt, dict):
        prompt = [prompt]
    if not isinstance(prompt, list):
        return ""

    parts: list[str] = []
    for block in prompt:
        if isinstance(block, str):
            parts.append(block)
            continue
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text = block.get("text")
            if isinstance(text, str):
                parts.append(text)
        elif block_type == "resource":
            resource = block.get("resource") or {}
            if isinstance(resource, dict):
                parts.append(_embedded_resource_to_markdown(resource))
        elif block_type == "resource_link":
            uri = block.get("uri")
            name = block.get("name") or uri
            if isinstance(uri, str):
                parts.append(f"Attached resource: {name}\nURI: {uri}")
        elif block_type in {"image", "audio"}:
            parts.append(f"[Unsupported ACP {block_type} content omitted.]")
    return "\n\n".join(part for part in parts if part)


def _embedded_resource_to_markdown(resource: dict[str, Any]) -> str:
    uri = resource.get("uri", "embedded-resource")
    mime_type = resource.get("mimeType")
    text = resource.get("text")
    if isinstance(text, str):
        fence = _fence_for_mime_type(mime_type)
        return f"Resource: {uri}\n\n```{fence}\n{text}\n```"
    blob = resource.get("blob")
    if isinstance(blob, str):
        return f"Resource: {uri}\n\n[Binary resource omitted: {mime_type or 'unknown mime type'}]"
    return f"Resource: {uri}"


def _fence_for_mime_type(mime_type: Any) -> str:
    if not isinstance(mime_type, str):
        return ""
    if "python" in mime_type:
        return "python"
    if "javascript" in mime_type:
        return "javascript"
    if "typescript" in mime_type:
        return "typescript"
    if "json" in mime_type:
        return "json"
    if "markdown" in mime_type:
        return "markdown"
    if "html" in mime_type:
        return "html"
    if "css" in mime_type:
        return "css"
    return ""


def _title_from_task(task: str) -> str:
    first_line = task.strip().splitlines()[0] if task.strip() else "New ACP session"
    title = " ".join(first_line.split())
    if len(title) > 80:
        title = f"{title[:77]}..."
    return title


def _is_team_run_output(value: Any) -> bool:
    return value.__class__.__name__ == "TeamRunOutput" and hasattr(value, "content")


def _output_to_text(output: Any) -> str:
    if output is None:
        return ""
    content = getattr(output, "content", output)
    return _stringify_content(content)


def _run_input_to_text(run: Any) -> str:
    run_input = getattr(run, "input", None)
    if run_input is None:
        return ""
    if hasattr(run_input, "input_content_string"):
        return run_input.input_content_string()
    return _stringify_content(getattr(run_input, "input_content", run_input))


def _stringify_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if hasattr(content, "to_dict"):
        try:
            return json.dumps(content.to_dict(), ensure_ascii=False)
        except Exception:
            return str(content)
    if isinstance(content, (dict, list)):
        return json.dumps(content, ensure_ascii=False)
    return str(content)


def _plan_entries_from_tasks(tasks: Any) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not tasks:
        return entries
    for task in tasks:
        content = getattr(task, "title", None) or getattr(task, "description", None)
        if not content:
            continue
        entries.append(
            {
                "content": str(content),
                "priority": "medium",
                "status": _normalize_plan_status(getattr(task, "status", None)),
            }
        )
    return entries


def _plan_entry_from_event(event: Any) -> dict[str, str] | None:
    content = getattr(event, "title", None) or getattr(event, "description", None)
    if not content:
        return None
    return {
        "content": str(content),
        "priority": "medium",
        "status": _normalize_plan_status(getattr(event, "status", None)),
    }


def _normalize_plan_status(status: Any) -> str:
    text = str(status or "pending").lower()
    if text in {"running", "active", "in-progress", "in_progress"}:
        return "in_progress"
    if text in {"done", "success", "succeeded", "failed", "error", "completed", "complete"}:
        return "completed"
    return "pending"


def _normalize_tool_status(status: str) -> str:
    if status == "failed":
        return "failed"
    if status == "completed":
        return "completed"
    if status == "cancelled":
        return "cancelled"
    return "in_progress"


def _tool_call_id(tool: Any) -> str:
    for attr in ("tool_call_id", "call_id", "id"):
        value = getattr(tool, attr, None)
        if value:
            return str(value)
    return f"tool_{uuid4().hex}"


def _tool_title(tool: Any) -> str:
    if tool is None:
        return "Run tool"
    for attr in ("tool_name", "function_name", "name"):
        value = getattr(tool, attr, None)
        if value:
            return str(value)
    return "Run tool"


def _tool_input(tool: Any) -> dict[str, Any]:
    if tool is None:
        return {}
    for attr in ("tool_args", "arguments", "input"):
        value = getattr(tool, attr, None)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return {"value": value}
    return {}


def _tool_output(tool: Any) -> dict[str, Any]:
    if tool is None:
        return {}
    for attr in ("result", "content", "output"):
        value = getattr(tool, attr, None)
        if isinstance(value, dict):
            return value
        if value is not None:
            return {"value": _stringify_content(value)}
    return {}
