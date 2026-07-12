#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import sys
from provider_common import SYSTEM, parse_decision, post_json

key = os.environ.get("OPENAI_API_KEY")
model = os.environ.get("OPENAI_MODEL")
if not key or not model:
    raise SystemExit("OPENAI_API_KEY and OPENAI_MODEL are required")
url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/responses"
for line in sys.stdin:
    case = json.loads(line)
    payload = {
        "model": model,
        "instructions": SYSTEM,
        "input": json.dumps(case, ensure_ascii=False),
        "text": {"format": {"type": "json_schema", "name": "sdd_decision", "strict": True,
            "schema": {"type": "object", "additionalProperties": False,
                "required": ["case_id", "decision", "reason", "human_escalation"],
                "properties": {"case_id": {"type": "string"}, "decision": {"enum": ["allow", "block", "refuse", "escalate"]},
                    "reason": {"type": "string"}, "human_escalation": {"type": "boolean"}}}}}
    }
    response = post_json(url, {"Authorization": f"Bearer {key}"}, payload)
    text = response.get("output_text")
    if not text:
        text = next(part["text"] for item in response.get("output", []) for part in item.get("content", []) if part.get("type") == "output_text")
    print(json.dumps(parse_decision(text, case["case_id"]), ensure_ascii=False), flush=True)
