# Email Summary and Action Items Skill

[中文](README.zh-CN.md) | English

[![test](https://github.com/xiangri678/email-summary-action-items-skill/actions/workflows/test.yml/badge.svg)](https://github.com/xiangri678/email-summary-action-items-skill/actions/workflows/test.yml)

An Agent Skill for fetching authorized mailboxes read-only and using an AI model to produce an evidence-backed summary with thread context, source links, decisions, and action items.

## Contents

- `SKILL.md`: read-only summary workflow and mailbox boundaries
- `references/message-contract.md`: normalized message fields
- `references/summary-template.md`: summary structure
- `scripts/fetch_imap.py`: read-only multi-account IMAP collection
- `scripts/validate_messages.py`: validate normalized message JSON
- `scripts/summarize_emails.py`: generate a Chinese brief through an OpenAI-compatible API
- `scripts/validate_summary.py`: verify sections and message evidence references
- `examples/`: account configuration, fictional input, and expected output
- `tests/`: MIME parsing, thread grouping, and model-request tests
- `agents/openai.yaml`: UI metadata

IMAP collection uses read-only folder selection and `BODY.PEEK[]`. The pipeline does not mark messages read, archive, label, delete, reply, forward, or send mail.

## Use

Run the offline validation and AI dry run with the commands in [`examples/README.md`](examples/README.md). The same guide covers authorized IMAP collection and a real OpenAI-compatible model call.

## Authorship

Based on practical experience with Hermes Agent workflows. Email providers and clients retain their own terms and licenses.

## License

[MIT](LICENSE)
