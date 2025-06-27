import streamlit as st
from src.ai_core import get_ai_response_stream
from src.utils import correct_references

# --- 页面配置 ---
st.set_page_config(
    page_title="Gemini 联网搜索聊天",
    page_icon="🤖",
    layout="wide",
)

# --- 侧边栏 ---
with st.sidebar:
    st.header("模型配置")
    # 修正模型名称，使用官方要求的 "models/" 前缀
    # 移除了不存在的占位模型，以避免 API 错误
    model_options = {
        "Gemini 2.5 Flash (推荐)": "models/gemini-2.5-flash",
        "Gemini 2.0 Flash": "models/gemini-2.0-flash-001",
    }
    
    # 初始化模型选择
    if "selected_model" not in st.session_state or st.session_state.selected_model not in model_options.values():
        st.session_state.selected_model = "models/gemini-2.5-flash"

    # 获取当前模型的显示名称
    current_model_key = [key for key, value in model_options.items() if value == st.session_state.selected_model][0]

    # 创建模型选择下拉框
    selected_model_key = st.selectbox(
        "选择一个 Gemini 模型:",
        options=list(model_options.keys()),
        index=list(model_options.keys()).index(current_model_key) # 根据会话状态设置默认值
    )
    st.session_state.selected_model = model_options[selected_model_key]

    st.markdown("---")
    st.markdown("这是一个使用 Gemini API 构建的联网搜索聊天机器人。")
    st.markdown("它能够理解您的问题，上网搜索相关信息，并根据搜索结果生成回答，同时提供信息来源。")


# --- 页面标题 ---
st.title("🤖 Gemini 联网搜索聊天 (Pro)")
st.caption(f"一个能展示思考过程并引用来源的AI聊天机器人 (当前模型: {selected_model_key})")




# --- 初始化聊天状态 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我可以联网查询最新信息，并告诉你我的信息来源。"}
    ]

# --- 显示历史消息 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 聊天输入框 ---
if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ""
        response_placeholder = st.empty()
        citations_from_api = []
        
        try:
            response_stream = get_ai_response_stream(prompt, model_name=st.session_state.selected_model)
            
            for event in response_stream:
                if event["type"] == "tool_call":
                    st.info(f"🔍 正在搜索: `{event['query']}`")
                
                elif event["type"] == "text_chunk":
                    full_response += event["chunk"]
                    response_placeholder.markdown(full_response + "▌")
                
                elif event["type"] == "final_response":
                    citations_from_api = event.get("citations", [])
                    final_corrected_text = correct_references(full_response, citations_from_api)
                    response_placeholder.markdown(final_corrected_text)
                    full_response = final_corrected_text

                elif event["type"] == "error":
                    st.error(event["message"])
                    full_response = event["message"]
                    break
            
        except Exception as e:
            st.error(f"应用出现严重错误: {e}")
            full_response = "应用出现严重错误，请检查后台日志。"

    st.session_state.messages.append({"role": "assistant", "content": full_response})