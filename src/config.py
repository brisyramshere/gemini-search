
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
你是一个能联网的AI助理，你需要用中文回答问题。
当你需要网络搜索时，请使用 search_tool。
在回答的最后，请务必严格按照以下格式将你查找的资料链接作为参考资料附上：
[1] [标题](链接)
[2] [标题](链接)
...
""",
    "report_prompt": """
请根据以上对话内容，总结生成一份详细的调研报告。
报告需要包含以下部分：
1.  **摘要**: 简要概述调研的主题和核心发现。
2.  **引言**: 介绍调研的背景和目的。
3.  **主体**:
    *   分点详细阐述调研过程中的关键信息和发现。
    *   对每个要点进行深入分析和讨论。
    *   如果适用，可以包含数据、例子或图表。
4.  **结论**: 总结整个调研，并提出最终的观点或建议��
5.  **参考文献**: 列出所有在调研过程中引用的资料来源，格式如下：
    *   [1] [标题](链接)
    *   [2] [标题](链接)
    *   ...

请确保报告结构清晰、内容详实、语言专业。
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
