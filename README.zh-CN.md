# 邮件总结与待办提取 Skill

中文 | [English](README.md)

从一个或多个已授权邮箱生成有依据的邮件总结，保留会话上下文、原始邮件链接、决策和待办事项。

## 仓库内容

- `SKILL.md`：只读邮件总结流程与邮箱操作边界
- `SKILL.zh-CN.md`：中文 Skill 说明
- `references/message-contract.md`：统一邮件字段
- `references/digest-template.md`：总结模板
- `scripts/validate_messages.py`：在总结前验证统一邮件 JSON
- `examples/`：虚构邮件输入、调用提示和预期输出
- `agents/openai.yaml`：界面元数据

生成总结时不会自动标记已读、归档、加标签、删除、回复、转发或发送邮件。

## 使用

通过兼容 Agent Skills 的客户端安装本仓库，或将仓库复制到 Agent 的 Skills 目录。需要用户已授权的邮件 Connector 或 CLI。

无需连接真实邮箱即可运行示例：

```bash
python3 scripts/validate_messages.py examples/messages.example.json
```

完整调用提示和预期结果见 [`examples/README.md`](examples/README.md)。

## 作者

由 Xiangri 根据自己构建的 Hermes Agent 工作流整理。邮件服务商与客户端仍遵循各自的条款与许可证。

## 许可证

[MIT](LICENSE)
