from __future__ import annotations
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,]+"), r"\1[REDACTED:TOKEN]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "[REDACTED:API_KEY]"),
    (re.compile(r"(?i)(api[_-]?key|password|secret)(\s*[=:]\s*)[^\s,;]+"), r"\1\2[REDACTED:SECRET]"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED:EMAIL]"),
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def redact(value):
    if isinstance(value, dict):
        return {k: ("[REDACTED:SECRET]" if re.search(r"(?i)api[_-]?key|password|secret|token", k) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        for pattern, replacement in SECRET_PATTERNS:
            value = pattern.sub(replacement, value)
    return value

class AuditRun:
    def __init__(self, root: Path, change_id: str, agent_id: str, provider: str, model: str,
                 instruction_version: str, context_sources: list[Path]):
        self.root = root
        self.run_id = "RUN-" + uuid.uuid4().hex.upper()
        self.dir = root / "reports" / "runs" / self.run_id
        self.dir.mkdir(parents=True, exist_ok=False)
        sources = []
        for source in context_sources:
            content = source.read_bytes()
            sources.append({"uri": str(source.relative_to(root)).replace("\\", "/"),
                            "sha256": hashlib.sha256(content).hexdigest(), "classification": "internal"})
        self.context = {"run_id": self.run_id, "sources": sources}
        self.tools: list[dict] = []
        self.guardrails: list[dict] = []
        self.run = {"run_id": self.run_id, "change_id": change_id, "task_id": None,
                    "agent_id": agent_id, "started_at": now(), "ended_at": None, "status": "running",
                    "model": {"provider": provider, "name": model, "version": "runtime"},
                    "instruction_version": instruction_version,
                    "context_sources": [s["uri"] for s in sources], "tool_events": [],
                    "guardrail_events": [], "usage": {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0},
                    "human_escalation": None}
        self._write()

    def record_tool(self, tool: str, action: str, decision: str, request, response=None, duration_ms: int = 0, error=None):
        item = {"event_id": "TLE-" + uuid.uuid4().hex.upper(), "run_id": self.run_id,
                "occurred_at": now(), "tool": tool, "action": action, "decision": decision,
                "request_sha256": digest(redact(request)), "response_sha256": digest(redact(response)) if response is not None else None,
                "duration_ms": duration_ms, "error": redact(error)}
        self.tools.append(item); self.run["tool_events"].append(item["event_id"]); self._write()

    def record_guardrail(self, guardrail: str, outcome: str, subject, reason: str):
        item = {"event_id": "GRE-" + uuid.uuid4().hex.upper(), "run_id": self.run_id,
                "occurred_at": now(), "guardrail": guardrail, "outcome": outcome,
                "subject_sha256": digest(redact(subject)), "reason": redact(reason)}
        self.guardrails.append(item); self.run["guardrail_events"].append(item["event_id"]); self._write()

    def finalize(self, status: str, output, human_escalation=None, usage=None):
        self.run["status"] = status; self.run["ended_at"] = now()
        self.run["human_escalation"] = redact(human_escalation)
        if usage: self.run["usage"].update(usage)
        (self.dir / "final-output.json").write_text(json.dumps(redact(output), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._write()

    def _write(self):
        (self.dir / "run.json").write_text(json.dumps(self.run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.dir / "context-manifest.json").write_text(json.dumps(self.context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.dir / "tool-events.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in self.tools), encoding="utf-8")
        (self.dir / "guardrail-events.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in self.guardrails), encoding="utf-8")
