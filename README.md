# Gemini 联网搜索与报告生成助理

这是一个基于 Google Gemini API 构建的高级 AI 助理。它不仅能通过联网搜索提供附带引用来源的实时回答，还能将多轮对话内容一键合成为结构化的研究报告。应用支持高度定制化，允许用户通过图形界面直接调整模型、API端点和系统提示词。

## ✨ 功能特性

- **🌐 实时联网搜索**: 利用 Google 搜索工具，确保回答基于最新的、可验证的信息。
- **🔗 清晰引用来源**: 在回答中自动标注信息来源 `[^N]`，并在末尾附上可点击的引用链接，保证内容的可信度和可追溯性。
- **📝 一键生成研究报告**: 可将当前对话的完整内容（包含问、答、引用）作为上下文，调用高级模型（如 Gemini 2.5 Pro）生成一份综合性的研究报告。
- **⚙️ 高度可配置**:
  - **模型切换**: 可在 UI 上为“搜索”和“报告生成”任务独立选择不同的 Gemini 模型。
  - **自定义提示词**: 允许用户直接在设置中修改和保存系统提示词（System Prompt）和报告生成提示词。
  - **API 端点配置**: 支持自定义 API Endpoint，方便通过代理或私有网���访问。
- **��� 完整对话管理**:
  - **多对话管理**: 在侧边栏轻松创建、切换和删除多个独立的对话。
  - **消息级操作**: 可以删除对话中的任意单条消息。
  - **上下文记忆**: 支持多轮对话，实现连贯的上下文理解。
- **💾 对话持久化**:
  - **自动保存对话**: 所有对话历史自动保存到本地 `conversations.json` 文件。
  - **配置持久化**: 所有设置（API密钥、模型、提示词等）自动保存到本地 `config.json` 文件。
- **💨 流式响应**: 实时显示 AI 的思考过程（例如，正在搜索什么）和逐字生成的回答，提供流畅的交互体验。
- **📥 导出对话**: 可随时将当前对话的完整内容下载为 Markdown 文件。
- **🖥️ 双重界面**:
  - **Web 界面**: 基于 Streamlit 构建，提供丰富的图形化聊天与管理体验。
  - **终端应用**: 提供一个纯命令行的聊天版本，方便开发者进行快速调试和测试。

## 🚀 技术架构

项目采用模块化的代码结构，清晰地分离了前端界面、核心逻辑和配置管理。

- **前端应用**:
  - `app.py`: 使用 **Streamlit** 实现的主要 Web 应用，负责所有用户交互、设置管理和界面展示。
  - `console_app.py`: 一个基于 **Rich** 库的纯终端应用，用于快速���试和验��核心功能。

- **核心后端 (`src/`)**:
  - `src/ai_core.py`: 项目的核心，封装了与 **Google Gemini API** 的所有交互。它负责构建请求、调用搜索工具、处理流式响应，并实现了独立的聊天和报告生成逻辑。
  - `src/config.py`: 实现了完整的配置管理系统。它使用 `config.json` 来持久化存储所有设置，并提供了在应用运行时动态读取和更新配置的接口。
  - `src/utils.py`: 包含数据持久化的辅助函数，负责读写 `conversations.json` 文件。

- **依赖管理**:
  - `requirements.txt`: 明确列出了项目所需的所有 Python 依赖库。

## 快速开始

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/your-username/gemini-search-agent.git
    cd gemini-search-agent
    ```

2.  **安装依赖**:
    ```bash
    # 建议在虚拟环境中操作
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **运行 Web 应用**:
    ```bash
    streamlit run app.py
    ```

4.  **配置 API 密钥**:
    - 应用启动后，在浏览器中打开。
    - 点击侧边栏右上角的 **⚙** 图标，打开设置面板。
    - 在 "Gemini API Key" 输入框中填入您的 Google API 密钥。
    - 点击 "保存设置"。应用现在即可正常使用。

5.  **(可选) 运行终端应用**:
    ```bash
    python console_app.py
    ```
    *注意：终端应用会复用您在 Web 界面中保存的 `config.json` 配置。*

## 截图

*Web 界面 - 主聊天窗口*
![Web Interface](https://path-to-your-screenshot/web_interface.png)

*Web 界面 - 设置面板*
![Settings Panel](https://path-to-your-screenshot/settings_panel.png)

*终端应用截图*
![Console App](https://path-to-your-screenshot/console_app.png)
