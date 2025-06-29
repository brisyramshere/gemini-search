
import json
import os
import streamlit as st

# 定义配置文件的路径
CONFIG_FILE = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "api_endpoint": "https://generativelanguage.googleapis.com",
    "api_key": "",
    "search_model": "models/gemini-2.5-flash",
    "report_model": "models/gemini-2.5-pro",
    "system_prompt": """
You are a helpful and informative AI assistant that provides answers grounded in web search results.
When you answer, you MUST cite your sources.
For each piece of information you provide, add a citation marker in the format [^N] where N is the number of the source.
At the end of your entire response, provide a 'References:' section.
Under the 'References:' section, list all the sources you used as a standard Markdown numbered list.
Each item in the list should be in the format: `1. [Source Title](URL)`.

Example:
The sky is blue due to a phenomenon called Rayleigh scattering [^1].

References:
1. [What Makes the Sky Blue?](https://www.space.com/what-makes-the-sky-blue)
""",
    "report_prompt": """
You are a professional researcher and analyst.
Your task is to synthesize the provided conversation history into a comprehensive and well-structured research report.
The conversation history contains user questions, AI answers, and citation markers (e.g., [^1], [^2]).

**Your task is to act as a summarizer and organizer, not a new researcher.**
**DO NOT perform any new web searches.** Base your report EXCLUSIVELY on the information and sources already present in the conversation history.

Follow these steps:
1. **Review and Synthesize**: Thoroughly review the entire conversation history to understand the key topics, findings, and all cited sources.
2. **Structure and Write**: Draft a formal report in Markdown format with a clear structure, including an introduction, key findings, detailed analysis, and a conclusion. 
3. **Cite Everything**: CRITICALLY, every piece of information in your report must be accurately cited. Use the citation markers `[^N]` exactly as they appear in the original conversation. All citations must be consolidated and listed at the end of the report under a 'References' section.
4. **Demarcate the Report**: Start the actual report with a `---` separator. Before the separator, you can briefly outline your plan, but after the separator, only the report content should exist.
"""
}

def load_config():
    """从 JSON 文件加载配置。如果文件不存在，则创建并使用默认配置。"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                config_from_file = json.load(f)
            except json.JSONDecodeError:
                # 如果文件损坏或为空，则返回默认配置
                return DEFAULT_CONFIG
            # 与默认配置合并，这样即使添加了新的配置项，旧的配置文件也能兼容
            config = DEFAULT_CONFIG.copy()
            config.update(config_from_file)
            return config
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """将配置保存到 JSON 文件。"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def init_config():
    """在 Streamlit session state 中初始化配置"""
    if "config" not in st.session_state:
        st.session_state.config = load_config()

def get_config(key, default=None):
    """从 session state 获取配置项"""
    init_config()
    # 提供一个回退到默认值的机制，以防 key 不存在
    default_value = default if default is not None else DEFAULT_CONFIG.get(key)
    return st.session_state.config.get(key, default_value)


def update_config(key, value):
    """更新 session state 中的配置项并保存到文件"""
    init_config()
    st.session_state.config[key] = value
    save_config(st.session_state.config)

# 为了向后兼容旧的函数调用
def load_api_key():
    return get_config("api_key")

def load_base_url():
    return get_config("api_endpoint")

# 在模块加载时就获取提示词，以便其他模块导入时能直接使用
SYSTEM_PROMPT = get_config("system_prompt")
GENERATE_REPORT_PROMPT = get_config("report_prompt")
