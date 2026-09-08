# 使用示例 / Examples

先验证邮件 Connector 导出的统一 JSON：

```bash
python3 scripts/validate_messages.py examples/messages.example.json
```

然后让 Agent 使用本 Skill 处理该文件：

> 使用 `$email-summary-action-items` 总结 `examples/messages.example.json`，按照模板提取已确认决策、需要回复的事项和待办，并保留邮件来源链接。

预期结构见 [summary.example.md](summary.example.md)。真实运行时，Connector 负责搜索和读取邮件；本仓库负责数据契约、完整会话判断、总结结构和邮箱只读边界。

English prompt:

> Use `$email-summary-action-items` to summarize `examples/messages.example.json`, extract confirmed decisions and action items, and preserve source links.
