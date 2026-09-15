#!/usr/bin/env python3
"""Validate normalized email messages before summary generation."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path

REQUIRED = {"account", "message_id", "thread_id", "date", "from", "to", "subject", "body"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    messages = payload.get("messages") if isinstance(payload, dict) else payload
    if not isinstance(messages, list):
        raise SystemExit("input must be a JSON list or an object with a messages list")

    errors: list[str] = []
    ids: list[tuple[str, str]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            errors.append(f"item {index}: must be an object")
            continue
        missing = sorted(REQUIRED - message.keys())
        if missing:
            errors.append(f"item {index}: missing {', '.join(missing)}")
        for field in ("account", "message_id", "thread_id", "date"):
            if not str(message.get(field, "")).strip():
                errors.append(f"item {index}: {field} must not be empty")
        try:
            parsed = datetime.fromisoformat(str(message.get("date", "")).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append(f"item {index}: date must include a timezone")
        except ValueError:
            errors.append(f"item {index}: date is not ISO-8601")
        for field in ("from", "to"):
            if not isinstance(message.get(field), list):
                errors.append(f"item {index}: {field} must be a list")
        ids.append((str(message.get("account", "")), str(message.get("message_id", ""))))
    duplicates = [key for key, count in Counter(ids).items() if key[1] and count > 1]
    if duplicates:
        errors.append(f"duplicate account/message_id pairs: {duplicates}")

    result = {
        "valid": not errors,
        "messages": len(messages),
        "threads": len({(m.get("account"), m.get("thread_id")) for m in messages if isinstance(m, dict)}),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
