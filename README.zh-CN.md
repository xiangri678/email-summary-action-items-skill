# 邮件总结与待办提取 Skill

中文 | [English](README.md)

[![test](https://github.com/xiangri678/email-summary-action-items-skill/actions/workflows/test.yml/badge.svg)](https://github.com/xiangri678/email-summary-action-items-skill/actions/workflows/test.yml)

从一个或多个已授权邮箱生成有依据的邮件总结，保留会话上下文、原始邮件链接、决策和待办事项。

## 仓库内容

- `SKILL.md`：只读邮件总结流程与邮箱操作边界
- `SKILL.zh-CN.md`：中文 Skill 说明
- `references/message-contract.md`：统一邮件字段
- `references/summary-template.md`：总结模板
- `scripts/fetch_imap.py`：多账号 IMAP 只读采集和线程字段归一化
- `scripts/validate_messages.py`：在调用模型前验证邮件 JSON
- `scripts/summarize_emails.py`：通过 OpenAI-compatible API 生成完整中文文稿
- `scripts/validate_summary.py`：检查章节和 `[账号/邮件ID]` 证据引用
- `examples/`：邮箱配置、虚构邮件输入和预期输出
- `tests/`：MIME 解析、线程归并和模型请求测试
- `agents/openai.yaml`：界面元数据

采集使用 IMAP 只读模式和 `BODY.PEEK[]`。生成总结时不会自动标记已读、归档、加标签、删除、回复、转发或发送邮件。

## 使用

无需连接真实邮箱即可验证完整的本地输入与输出契约：

```bash
python3 scripts/validate_messages.py examples/messages.example.json
python3 scripts/summarize_emails.py \
  --input examples/messages.example.json \
  --date 2026-09-07 \
  --dry-run
python3 scripts/validate_summary.py \
  --input examples/summary.example.md \
  --messages examples/messages.example.json
```

真实闭环命令见 [`examples/README.md`](examples/README.md)，包括配置邮箱、只读获取邮件、AI 整理和验证文稿。

## 作者

由 Xiangri 根据自己构建的 Hermes Agent 工作流整理。邮件服务商与客户端仍遵循各自的条款与许可证。

## 许可证

[MIT](LICENSE)
