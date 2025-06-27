# 长期记忆

这是一个用于存储长期记忆和上下文信息的文件。

只在用户明确要求时更新此文件。

---

## Gemini 模型与工具兼容性

- **`google_search_retrieval`** 是一个旧的联网搜索工具，适用于旧版模型。
- **`google_search`** 是新的联网搜索工具。
- **Gemini 2.5 Flash** 及其他新模型需要使用新的 `google_search` 工具。在代码中，应通过 `Tool.from_google_search_retrieval()` 或类似方法来调用，而不是 `Tool(google_search_retrieval={})`。
- 如果新模型与旧工具一起使用，API 会返回 `400 Search Grounding is not supported` 错误。

---

## 项目配置

- **包管理器**: 项目使用 `uv` 作为包管理器。
- **`uv` 路径**: `uv` 的可执行文件位于 `~/.local/bin/uv`。
- **虚拟环境**: 项目依赖于一个虚拟环境，在执行任何 Python 脚本之前，需要使用 `source .venv/bin/activate` 来激活它。

---

## 核心原则

- **主动验证API用法**: 当遇到API用法错误（如参数错误、属性不存在等）时，必须优先使用联网搜索或Context7 MCP查询最新的官方API文档，以确认正确的用法，而不是仅依赖于自身的知识或反复试错。