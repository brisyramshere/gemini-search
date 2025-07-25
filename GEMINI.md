# 长期记忆

这是一个用于存储长期记忆和上下文信息的文件。

只在用户明确要求时更新此文件。

## 项目配置

- **包管理器**: 项目使用 `uv` 作为包管理器。
- **`uv` 路径**: `uv` 的可执行文件位于 `~/.local/bin/uv`。
- **虚拟环境**: 项目依赖于一个虚拟环境，在执行任何 Python 脚本之前，需要使用 `source .venv/bin/activate` 来激活它。

## Google Gemini API

- **正确的库**: 与 Google Gemini API 交互的正确 Python 库是 `google-genai`。
- **安装**: 使用 `uv pip install google-genai` 进行安装。
- **避免混淆**: 不要使用 `google-generativeai` 或 `python-genai`，它们是不正确的。

## 经验总结

- **主动验证API用法**: 当遇到API用法错误（如参数错误、属性不存在等）时，必须优先使用联网搜索或Context7查询最新的官方API文档，以确认正确的用法，而不是仅依赖于旧的知识或反复试错。
- **自定义 Base URL**: `genai.Client` 支持通过 `http_options` 参数设置自定义的 `base_url`，这对于通过代理或网关路由API请求至关重要。示例：`client = genai.Client(http_options={"base_url": "https://my-proxy.com"})`
- **严��遵循用户指定的环境和工具**: 必须始终遵循用户明确指定的工具和环境配置（例如，使用 `uv` 而不是 `pip`）。在执行任何操作前，必须确认并使用正确的环境（例如，通过 `source .venv/bin/activate` 激活虚拟环境）。
- **从简单到复杂，逐一验证**: 在实现复杂功能时，应从最简单的API调用开始验证，确保核心路径通畅后，再逐步增加参数和复杂性（例如，先验证无参数的 `generate_content`，再添加 `stream`、`config` 等）。这能更快地定位问题。
- **仔细阅读错误信息**: API返回的错误信息（如 `unexpected keyword argument 'stream'` 或 `takes 1 positional argument but 2 were given`）是解决问题的最直接线索。必须仔细分析错误信息，并将其与官方文档进行比对，而不是猜测问题所在。


- **先调用工具收集信息再开始写代码**：对于一些会实时更新的库的api的调用，一定要先搜索，包括gemini搜索和context7 mcp最新文档学习，确保掌握了精准无误的api用法，并学习了一些案例后在开始写代码；
- **擅长通过终端的输出进行自验证**:多想办法在终端输出一些调试信息，让自己可以基于终端信息进行多轮迭代和自验证，这样可以减少人工交互的干预。
- **事实胜于印象**：当遇到问题时，时刻记得使用搜索工具进行事实确认，或者采用增加调试log的方式确认更具体的错误信息，而非按照个人印象去盲目修改和尝试。
- **虚拟环境路径问题**: 当 `streamlit run` 或 `python` 命令失败并显示 `bad interpreter` 或 `command not found` 等错误时，通常意味着没有使用虚拟环境中的正确可执行文件。直接调用绝对路径（如 `.venv/bin/python` 或 `.venv/bin/streamlit`）可以确保使用正确的环境和依赖，是解决此类问题的可靠方法。

- **关于google-genai api引用信息的关键发现**：
   1. `grounding_metadata` 的结构: 在整个流式响应中，grounding_metadata
      对象始终存在，但它在前99%的块（chunk）中都是空的 ({}).
   2. 引用信息的位置: 只有在最后一个数据块中，grounding_metadata 才被填充内容。然而，它填充的是
      search_entry_point（用于UI展示）和 web_search_queries（模型执行的搜索词），里面并没有我们期望的 
      `citations` 列表。
   3. 引用由模型生成: 引用链接（1. 
      [Title](URL)）是由模型在回答的文本正文中直接生成的，而不是通过一个独立的、结构化的元数据字段提供的。