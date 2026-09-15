#!/usr/bin/env python3
"""Fetch messages from configured IMAP folders without changing mailbox state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email import policy
from email.header import decode_header
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
import hashlib
import html
import imaplib
import json
import os
from pathlib import Path
import re

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed


def imap_date(value: datetime) -> str:
    return f"{value.day:02d}-{MONTHS[value.month - 1]}-{value.year:04d}"


def decode_text(value: str | None) -> str:
    parts: list[str] = []
    for item, charset in decode_header(value or ""):
        if isinstance(item, bytes):
            parts.append(item.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(item)
    return "".join(parts).strip()


def addresses(value: str | None) -> list[str]:
    result: list[str] = []
    for name, address in getaddresses([value or ""]):
        decoded_name = decode_text(name)
        result.append(f"{decoded_name} <{address}>" if decoded_name else address)
    return [item for item in result if item]


def html_to_text(value: str) -> str:
    value = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", value, flags=re.I | re.S)
    value = re.sub(r"<(br|/p|/div|/li)\b[^>]*>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"[ \t]+", " ", value)
    return re.sub(r"\n{3,}", "\n\n", value).strip()


def message_body(message, max_chars: int) -> str:
    plain: list[str] = []
    rich: list[str] = []
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() not in {"text/plain", "text/html"}:
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeDecodeError):
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if part.get_content_type() == "text/plain":
            plain.append(str(content))
        else:
            rich.append(html_to_text(str(content)))
    value = "\n\n".join(plain or rich)
    value = re.sub(r"\n{3,}", "\n\n", value).strip()
    return value[:max_chars]


def message_time(message) -> datetime | None:
    try:
        value = parsedate_to_datetime(message.get("Date", ""))
    except (TypeError, ValueError, OverflowError):
        return None
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def header_ids(value: str | None) -> list[str]:
    return [item.strip("<>") for item in re.findall(r"<[^>]+>", value or "")]


def normalize_message(raw: bytes, account: str, folder: str, max_body_chars: int) -> dict | None:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    sent_at = message_time(message)
    if sent_at is None:
        return None
    raw_id = message.get("Message-ID", "").strip()
    stable_id = raw_id.strip("<>") or hashlib.sha256(raw).hexdigest()
    references = header_ids(message.get("References"))
    parents = header_ids(message.get("In-Reply-To"))
    parent = parents[0] if parents else ""
    attachments = [decode_text(part.get_filename()) for part in message.walk() if part.get_filename()]
    return {
        "account": account,
        "folder": folder,
        "message_id": stable_id,
        "thread_id": references[0] if references else parent or stable_id,
        "in_reply_to": parent,
        "references": references,
        "date": sent_at.isoformat(),
        "from": addresses(message.get("From")),
        "to": addresses(message.get("To")),
        "subject": decode_text(message.get("Subject")),
        "body": message_body(message, max_body_chars),
        "attachments": attachments,
        "provider_url": "",
    }


def raw_from_fetch(response) -> bytes | None:
    candidates = [item[1] for item in response if isinstance(item, tuple) and isinstance(item[1], bytes)]
    return max(candidates, key=len) if candidates else None


def quote_mailbox(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def collect(config: dict, start: datetime, end: datetime, max_per_folder: int, max_body_chars: int) -> dict:
    messages: list[dict] = []
    errors: list[dict] = []
    successful_folders = 0
    enabled = [account for account in config.get("accounts", []) if account.get("enabled", True)]
    if not enabled:
        raise ValueError("configuration has no enabled accounts")

    for account in enabled:
        name = account.get("name") or account.get("host") or "unnamed"
        username = os.environ.get(account.get("username_env", ""), "")
        password = os.environ.get(account.get("password_env", ""), "")
        if not username or not password:
            errors.append({"account": name, "folder": None, "error": "credential environment variable is missing"})
            continue
        connection = None
        try:
            if not account.get("ssl", True):
                raise ValueError("plaintext IMAP is not supported; configure an SSL endpoint")
            connection = imaplib.IMAP4_SSL(account["host"], int(account.get("port", 993)), timeout=30)
            connection.login(username, password)
            for folder in account.get("folders", ["INBOX"]):
                try:
                    status, _ = connection.select(quote_mailbox(folder), readonly=True)
                    if status != "OK":
                        raise RuntimeError("folder select failed")
                    query = f'(SINCE "{imap_date(start)}" BEFORE "{imap_date(end)}")'
                    status, data = connection.uid("search", None, query)
                    if status != "OK":
                        raise RuntimeError("UID search failed")
                    uids = (data[0] or b"").split()[-max_per_folder:]
                    for uid in uids:
                        status, response = connection.uid("fetch", uid, "(BODY.PEEK[])")
                        raw = raw_from_fetch(response) if status == "OK" else None
                        if not raw:
                            continue
                        normalized = normalize_message(raw, name, folder, max_body_chars)
                        if normalized:
                            sent_at = parse_time(normalized["date"])
                            if start <= sent_at < end:
                                messages.append(normalized)
                    successful_folders += 1
                except Exception as exc:
                    errors.append({"account": name, "folder": folder, "error": str(exc)})
        except Exception as exc:
            errors.append({"account": name, "folder": None, "error": str(exc)})
        finally:
            if connection is not None:
                try:
                    connection.logout()
                except Exception:
                    pass

    deduplicated = {(item["account"], item["message_id"]): item for item in messages}
    ordered = sorted(deduplicated.values(), key=lambda item: item["date"])
    known_ids = {(item["account"], item["message_id"]) for item in ordered}
    incomplete_threads = sorted(
        {
            (item["account"], item["thread_id"])
            for item in ordered
            if (item.get("references") or item.get("in_reply_to"))
            and (item["account"], item["thread_id"]) not in known_ids
        }
    )
    return {
        "meta": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "accounts": [account.get("name", "unnamed") for account in enabled],
            "successful_folders": successful_folders,
            "errors": errors,
            "incomplete_threads": [
                {"account": account, "thread_id": thread_id} for account, thread_id in incomplete_threads
            ],
            "read_only": True,
        },
        "messages": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--start", required=True, help="ISO-8601 inclusive timestamp with timezone")
    parser.add_argument("--end", required=True, help="ISO-8601 exclusive timestamp with timezone")
    parser.add_argument("--output", type=Path, default=Path("emails.json"))
    parser.add_argument("--max-per-folder", type=int, default=200)
    parser.add_argument("--max-body-chars", type=int, default=6000)
    args = parser.parse_args()
    start, end = parse_time(args.start), parse_time(args.end)
    if start >= end:
        parser.error("--start must be earlier than --end")
    if args.max_per_folder < 1 or args.max_body_chars < 1:
        parser.error("--max-per-folder and --max-body-chars must be positive")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    try:
        result = collect(config, start, end, args.max_per_folder, args.max_body_chars)
    except ValueError as exc:
        parser.error(str(exc))
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(result['messages'])} messages -> {output}")
    return 0 if result["meta"]["successful_folders"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
