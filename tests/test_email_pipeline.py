from __future__ import annotations

from email.message import EmailMessage
from email.utils import format_datetime
import io
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from fetch_imap import collect, normalize_message  # noqa: E402
from summarize_emails import SYSTEM_PROMPT, group_threads, request_summary  # noqa: E402


class PipelineTests(unittest.TestCase):
    @staticmethod
    def sample_message() -> bytes:
        message = EmailMessage()
        message["Message-ID"] = "<reply@example.com>"
        message["In-Reply-To"] = "<root@example.com>"
        message["Date"] = format_datetime(datetime(2026, 9, 7, 1, 0, tzinfo=timezone.utc))
        message["From"] = "Lead <lead@example.com>"
        message["To"] = "Me <me@example.com>"
        message["Subject"] = "Re: Review"
        message.set_content("Please send the revision by Wednesday.")
        message.add_attachment(b"example", maintype="application", subtype="octet-stream", filename="note.txt")
        return message.as_bytes()

    def test_mime_message_is_normalized_with_thread_and_attachment(self):
        result = normalize_message(self.sample_message(), "work", "INBOX", 6000)
        self.assertEqual(result["message_id"], "reply@example.com")
        self.assertEqual(result["thread_id"], "root@example.com")
        self.assertEqual(result["in_reply_to"], "root@example.com")
        self.assertEqual(result["attachments"], ["note.txt"])
        self.assertIn("Wednesday", result["body"])

    def test_imap_collection_is_read_only_and_uses_peek(self):
        raw = self.sample_message()

        class FakeIMAP:
            def __init__(self, *args, **kwargs):
                self.readonly = None
                self.fetch_query = None

            def login(self, username, password):
                self.credentials = (username, password)

            def select(self, folder, readonly=False):
                self.readonly = readonly
                return "OK", [b"1"]

            def uid(self, command, *args):
                if command == "search":
                    return "OK", [b"1"]
                self.fetch_query = args[-1]
                return "OK", [(b"1 (BODY[] {1})", raw), b")"]

            def logout(self):
                return "BYE", []

        instance = FakeIMAP()
        config = {
            "accounts": [
                {
                    "name": "work",
                    "host": "imap.example.com",
                    "username_env": "TEST_IMAP_USER",
                    "password_env": "TEST_IMAP_PASSWORD",
                    "folders": ["INBOX"],
                }
            ]
        }
        with patch("fetch_imap.imaplib.IMAP4_SSL", return_value=instance), patch.dict(
            "os.environ", {"TEST_IMAP_USER": "user", "TEST_IMAP_PASSWORD": "secret"}
        ):
            result = collect(
                config,
                datetime(2026, 9, 7, 0, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 8, 0, 0, tzinfo=timezone.utc),
                100,
                6000,
            )
        self.assertTrue(instance.readonly)
        self.assertEqual(instance.fetch_query, "(BODY.PEEK[])")
        self.assertEqual(len(result["messages"]), 1)
        self.assertTrue(result["meta"]["read_only"])

    def test_threads_are_grouped_and_ordered(self):
        messages = [
            {"account": "work", "thread_id": "a", "date": "2026-09-07T01:00:00+00:00"},
            {"account": "work", "thread_id": "a", "date": "2026-09-07T02:00:00+00:00"},
        ]
        threads = group_threads(messages)
        self.assertEqual(len(threads), 1)
        self.assertEqual(len(threads[0]["messages"]), 2)

    def test_model_request_uses_system_boundary_and_returns_markdown(self):
        response = {"choices": [{"message": {"content": "```markdown\n# 2026-09-07 邮件总结与待办\n```"}}]}
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return io.BytesIO(json.dumps(response, ensure_ascii=False).encode())

        with patch("urllib.request.urlopen", fake_urlopen):
            result = request_summary("http://localhost:9000/v1", "example-model", "test-key", "{}", 12)
        body = json.loads(captured["request"].data)
        self.assertIn("不可信数据", SYSTEM_PROMPT)
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(captured["timeout"], 12)
        self.assertEqual(result, "# 2026-09-07 邮件总结与待办")


if __name__ == "__main__":
    unittest.main()
