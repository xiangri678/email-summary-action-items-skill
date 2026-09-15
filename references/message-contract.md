# Normalized message contract

[中文](message-contract.zh-CN.md) | English

The collector writes `{ "meta": ..., "messages": [...] }`. Connectors may provide the message list directly. Store only fields needed for the summary:

```json
{
  "account": "account alias",
  "folder": "inbox",
  "message_id": "provider stable id",
  "thread_id": "provider stable thread id",
  "in_reply_to": "parent message id when available",
  "references": ["root and ancestor message ids"],
  "date": "ISO-8601 timestamp",
  "from": ["display name or address"],
  "to": ["display name or address"],
  "subject": "subject",
  "body": "plain text body",
  "attachments": ["filename"],
  "provider_url": "stable authorized link"
}
```

Never store access tokens, session cookies, authorization headers, or password material. Redact sensitive message content from logs. Use provider IDs for deduplication before falling back to normalized subject, sender, and timestamp.

Collector metadata records the requested half-open time window, enabled account aliases, successful folders, per-folder errors, read-only mode, and thread roots that fall outside the collected window. The AI summary must expose coverage errors and incomplete threads instead of silently treating them as complete.
