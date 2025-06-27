# Gemini 联网搜索聊天应用

这是一个使用 Streamlit 和 Gemini API 构建的简单聊天机器人，它具备联网搜索能力，可以回答关于最新事件的问题。

## 功能

- 实时聊天界面
- 基于Gemini Pro的智能回答
- 集成Google搜索以获取最新信息

## 技术栈

- **语言**: Python
- **框架**: Streamlit
- **AI模型**: Google Gemini 1.5 Flash
- **依赖管理**: uv

## 如何运行

1.  **克隆仓库**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **创建并激活虚拟环境**
    推荐使用 `uv` 来管理环境：
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **设置API密钥**
    - 将 `.env.example` 文件重命名为 `.env`。
    - 打开 `.env` 文件，将 `YOUR_API_KEY_HERE` 替换为您的真实Google API密钥。

5.  **运行应用**
    ```bash
    streamlit run app.py
    ```

    应用现在应该已经在您的浏览器中打开。
