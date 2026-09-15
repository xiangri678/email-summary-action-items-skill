#!/usr/bin/env python3
"""Validate the structure and evidence references of an AI email summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

REQUIRED_SECTIONS = [
    "## 今日速览",
    "## 需要处理",
    "## 已确认决策与承诺",
    "## 等待他人",
    "## 重要信息",
    "## 低优先级",
    "## 来源与覆盖限制",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--messages", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("email-summary-validation.json"))
    args = parser.parse_args()
    markdown = args.input.read_text(encoding="utf-8")
    payload = json.loads(args.messages.read_text(encoding="utf-8"))
    messages = payload.get("messages", []) if isinstance(payload, dict) else payload
    known = {str(item.get("message_id", "")) for item in messages}

    errors: list[str] = []
    if not re.search(r"^# \d{4}-\d{2}-\d{2} 邮件总结与待办$", markdown, flags=re.M):
        errors.append("标题格式不符合要求")
    for section in REQUIRED_SECTIONS:
        if section not in markdown:
            errors.append(f"缺少章节：{section}")
    cited = set(re.findall(r"\[[^/\]\n]+/([^\]\n]+)\]", markdown))
    unknown = sorted(cited - known)
    if unknown:
        errors.append("引用了输入中不存在的邮件 ID：" + ", ".join(unknown))
    if messages and not cited:
        errors.append("没有找到 [账号/邮件ID] 证据引用")

    result = {"valid": not errors, "cited_message_ids": sorted(cited), "errors": errors}
    report = args.report.expanduser().resolve()
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("VALID" if result["valid"] else "INVALID")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
