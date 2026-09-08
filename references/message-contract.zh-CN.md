# 统一邮件字段规范

中文 | [English](message-contract.md)

只保存生成总结所需的字段：

```json
{
  "account": "邮箱别名",
  "folder": "inbox",
  "message_id": "服务商稳定邮件 ID",
  "thread_id": "服务商稳定会话 ID",
  "date": "ISO-8601 时间",
  "from": ["显示名或地址"],
  "to": ["显示名或地址"],
  "subject": "主题",
  "body": "纯文本正文",
  "attachments": ["文件名"],
  "provider_url": "已授权的稳定链接"
}
```

不得保存访问 Token、会话 Cookie、Authorization Header 或密码材料。日志中需要隐藏敏感邮件正文。优先使用服务商 ID 去重；缺少 ID 时再使用规范化主题、发件人和时间组合。
