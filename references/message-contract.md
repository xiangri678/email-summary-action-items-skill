# Normalized message contract

Store only fields needed for the digest:

```json
{
  "account": "account alias",
  "folder": "inbox",
  "message_id": "provider stable id",
  "thread_id": "provider stable thread id",
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
