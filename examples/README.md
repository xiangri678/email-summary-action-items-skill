# 使用示例 / Examples

## 1. 不连接邮箱的本地演示

验证虚构邮件、查看 AI 请求规模，并校验预期文稿：

```bash
python3 scripts/validate_messages.py examples/messages.example.json
python3 scripts/summarize_emails.py \
  --input examples/messages.example.json \
  --date 2026-09-07 \
  --dry-run
python3 scripts/validate_summary.py \
  --input examples/summary.example.md \
  --messages examples/messages.example.json \
  --report /tmp/email-summary-validation.json
```

## 2. 多邮箱只读采集

复制配置并启用需要的账号：

```bash
cp examples/accounts.example.json accounts.json
```

在 `accounts.json` 中把相应账号的 `enabled` 改为 `true`，然后设置配置里指定的用户名和应用专用密码环境变量。例如：

```bash
export GMAIL_IMAP_USERNAME='user@example.com'
export GMAIL_IMAP_PASSWORD='app-password'
python3 scripts/fetch_imap.py \
  --config accounts.json \
  --start '2026-09-14T07:00:00+08:00' \
  --end '2026-09-15T07:00:00+08:00' \
  --output emails.json
python3 scripts/validate_messages.py emails.json
```

脚本以 IMAP 只读模式打开文件夹，并用 `BODY.PEEK[]` 读取正文。不同服务商的“已发送”目录名称可能不同，应以实际 IMAP 目录为准。

## 3. AI 整理为完整文稿

选择用户允许接收这些邮件内容的 OpenAI-compatible 服务商：

```bash
export OPENAI_BASE_URL='https://provider.example/v1'
export OPENAI_MODEL='model-name'
export OPENAI_API_KEY='api-key'
python3 scripts/summarize_emails.py \
  --input emails.json \
  --date 2026-09-15 \
  --output email-summary.md
python3 scripts/validate_summary.py \
  --input email-summary.md \
  --messages emails.json \
  --report email-summary-validation.json
```

模型脚本按完整会话归并邮件，要求输出负责人、截止时间和决策时引用 `[账号/邮件ID]`。验证脚本会拒绝缺少固定章节、没有证据引用或引用不存在邮件 ID 的文稿。

也可以让 Agent 复核结果：

> 使用 `$email-summary-action-items` 检查 `email-summary.md` 和 `emails.json`，复核负责人、截止时间、决策与来源引用；不要发送邮件或改变邮箱状态。

预期结构见 [summary.example.md](summary.example.md)。凭据、`accounts.json`、真实邮件和生成文稿均已加入 `.gitignore`，不得提交到仓库。

English prompt:

> Use `$email-summary-action-items` to audit `email-summary.md` against `emails.json`, verify owners, deadlines, decisions, and evidence references, and keep the mailbox unchanged.
