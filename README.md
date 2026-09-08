# Email Summary and Action Items Skill

[中文](README.zh-CN.md) | English

An Agent Skill for producing evidence-backed digests across authorized mailboxes while preserving thread context, source links, decisions, and action items.

## Contents

- `SKILL.md`: read-only digest workflow and mailbox boundaries
- `references/message-contract.md`: normalized message fields
- `references/digest-template.md`: digest structure
- `agents/openai.yaml`: UI metadata

Digest generation does not mark messages read, archive, label, delete, reply, forward, or send mail.

## Use

Install this repository with an Agent Skills-compatible client, or copy the repository into your agent's skills directory. An authorized email connector or CLI is required.

## Authorship

Created by Xiangri from a self-built Hermes Agent workflow. Email providers and clients retain their own terms and licenses.

## License

[MIT](LICENSE)
