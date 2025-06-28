# Gemini 联网搜索聊天机器人

这是一个使用 Google Gemini API 构建的联网搜索聊天机器人。它能够理解用户的问题，通过联网搜索获取最新的信息，并以流式的方式生成附带引用来源的回答。

## ✨ 功能特性

- **🌐 实时联网搜索**: 利用 Google 搜索工具，确保回答基于最新的信息。
- **🔗 引用与来源**: 在回答中清晰地标注信息来源，并在末尾附上可点击的引用链接，保证内容的可信度和可追溯性。
- **💬 对话历史与上下文记忆**: 支持多轮对话，并能记住之前的交流内容，实现连贯的上下文理解。
- **💾 对话持久化存储**: 自动将所有对话历史保存到本地 JSON 文件，确保应用重启后数据不会丢失。
- **🗂️ 多对话管理**: 可以在侧边栏轻松创建、切换和管理多个独立的对话。
- **💨 流式响应**: 实时显示 AI 的思考过程（例如，正在搜索什么）和逐字生成的回答，提供流畅的交互体验。
- **🤖 多模型支持**: 支持在不同的 Gemini 模型（如 Gemini 2.5 Pro, Gemini 2.5 Flash）之间轻松切换。
- **🖥️ 双重界面**:
  - **Web 界面**: 基于 Streamlit 构建，提供丰富的图形化聊天体验。
  - **终端应用**: 提供一个纯命令行的聊天版本，方便开发者进行快速调试和测试。

## 🚀 技术架构

本项目采用模块化的代码结构，清晰地分离了前端界面、核心逻辑和配置。

- **前端应用**:
  - `app.py`: 使用 **Streamlit** 实现的主要 Web 应用，负责用户交互和���面展示。
  - `console_app.py`: 一个基于 **Rich** 库的纯终端应用，用于快速调试和验证核心功能。

- **核心后端 (`src/`)**:
  - `src/ai_core.py`: 项目的核心，封装了与 **Google Gemini API** 的所有交互。它负责构建请求、调用搜索工具、处理流式响应并提取引用数据。
  - `src/config.py`: 通过 **python-dotenv** 管理敏感配置（如 API 密钥），实现了配置与代码的分离。
  - `src/utils.py`: 包含辅助工具函数，例如 `correct_references`，用于解析和修正从 API 返回的引用链接，确保其格式正确。

- **依赖管理**:
  - `requirements.txt`: 明确列出了项目所需的所有 Python 依赖库。

## 快速开始

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/your-username/gemini-search-agent.git
    cd gemini-search-agent
    ```

2.  **创建并配置环境**:
    - 创建一个 `.env` 文件，并填入你的 Google API 密钥:
      ```
      GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
      ```
    - (可选) 如果你需要通过代理访问，可以额外配置 `API_BASE_URL`。

3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **运行应用**:
    - **Web 应用**:
      ```bash
      streamlit run app.py
      ```
    - **终端调试应用**:
      ```bash
      python console_app.py
      ```

## 截图

*Web 界面截图*
![Web Interface](https://path-to-your-screenshot/web_interface.png)

*终端应用截图*
![Console App](https://path-to-your-screenshot/console_app.png)