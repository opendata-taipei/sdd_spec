#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import sys
from provider_common import SYSTEM, parse_decision, post_json

key = os.environ.get("ANTHROPIC_API_KEY")
model = os.environ.get("ANTHROPIC_MODEL")
if not key or not model:
    raise SystemExit("ANTHROPIC_API_KEY and ANTHROPIC_MODEL are required")
url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages"
for line in sys.stdin:
    case = json.loads(line)
    response = post_json(url, {"x-api-key": key, "anthropic-version": "2023-06-01"}, {
        "model": model, "max_tokens": 512, "system": SYSTEM,
        "messages": [{"role": "user", "content": json.dumps(case, ensure_ascii=False)}],
    })
    text = "".join(part.get("text", "") for part in response.get("content", []) if part.get("type") == "text")
    print(json.dumps(parse_decision(text, case["case_id"]), ensure_ascii=False), flush=True)
