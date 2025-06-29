import streamlit as st
from src.ai_core import get_ai_response_stream
from src.utils import correct_references, save_conversations_to_file, load_conversations_from_file

# --- 页面配置 ---
st.set_page_config(
    page_title="Gemini 联网搜索聊天",
    page_icon="🤖",
    layout="wide",
)

# --- 加载或初始化对话 ---
def initialize_conversations():
    conversations_data = load_conversations_from_file()
    if conversations_data:
        st.session_state.conversations = conversations_data["conversations"]
        st.session_state.current_conversation_id = conversations_data["current_conversation_id"]
        st.session_state.next_conversation_id = conversations_data["next_conversation_id"]
    else:
        st.session_state.conversations = {
            "1": {"title": "新对话 1", "messages": [{"role": "assistant", "content": "你好！我可以联网查询最新信息，并告诉你我的信息来源。"}]}
        }
        st.session_state.current_conversation_id = "1"
        st.session_state.next_conversation_id = 2
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })

if "conversations" not in st.session_state:
    initialize_conversations()

# --- 侧边栏 ---
with st.sidebar:
    st.header("模型配置")
    model_options = {
        "Gemini 2.5 Pro (推荐)": "models/gemini-2.5-pro",
        "Gemini 2.5 Flash": "models/gemini-2.5-flash",
        "Gemini 2.0 Flash": "models/gemini-2.0-flash-001",
    }
    
    if "selected_model" not in st.session_state or st.session_state.selected_model not in model_options.values():
        st.session_state.selected_model = "models/gemini-2.5-pro"

    current_model_key = [key for key, value in model_options.items() if value == st.session_state.selected_model][0]

    selected_model_key = st.selectbox(
        "选择一个 Gemini 模型:",
        options=list(model_options.keys()),
        index=list(model_options.keys()).index(current_model_key)
    )
    st.session_state.selected_model = model_options[selected_model_key]

    st.markdown("---")

    st.header("对话管理")

    def create_new_conversation():
        conv_id = str(st.session_state.next_conversation_id)
        st.session_state.conversations[conv_id] = {
            "title": f"新对话 {conv_id}",
            "messages": [{"role": "assistant", "content": "你好！这是一个新的对话。"}]
        }
        st.session_state.current_conversation_id = conv_id
        st.session_state.next_conversation_id += 1
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })

    if st.button("➕ 新对话"):
        create_new_conversation()

    conversation_options = {conv_id: data["title"] for conv_id, data in st.session_state.conversations.items()}
    
    def on_conversation_change():
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })

    st.session_state.current_conversation_id = st.selectbox(
        "选择一个对话:",
        options=list(conversation_options.keys()),
        format_func=lambda conv_id: conversation_options[conv_id],
        index=list(conversation_options.keys()).index(st.session_state.current_conversation_id),
        on_change=on_conversation_change
    )

    st.markdown("---")
    st.markdown("这是一个使用 Gemini API 构建的联网搜索聊天机器人。")
    st.markdown("它能够理解您的问题，上网搜索相关信息，并根据搜索结果生成回答，同时提供信息来源。")


# --- 页面标题 ---
st.title("🤖 Gemini 联网搜索聊天 (Pro)")
current_conversation_title = st.session_state.conversations[st.session_state.current_conversation_id]["title"]
st.header(f"{current_conversation_title}")
st.caption(f"一个能展示思考过程并引用来源的AI聊天机器人 (当前模型: {selected_model_key})")


# --- 获取当前对话 ---
current_conversation = st.session_state.conversations[st.session_state.current_conversation_id]


# --- 显示历史消息 ---
for message in current_conversation["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 聊天输入框 ---
if prompt := st.chat_input("请输入您的问题..."):
    current_conversation["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ""
        response_placeholder = st.empty()
        citations_from_api = []
        
        # 准备历史消息 (除了最后一条用户消息)
        history = current_conversation["messages"][:-1]

        try:
            response_stream = get_ai_response_stream(prompt, model_name=st.session_state.selected_model, history=history)
            
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

    current_conversation["messages"].append({"role": "assistant", "content": full_response})

    # 更新对话标题 (如果这是第一条用户消息)
    if len(current_conversation["messages"]) == 3: # assistant + user + assistant
        current_conversation["title"] = prompt[:30] + "..." if len(prompt) > 30 else prompt
    
    save_conversations_to_file({
        "conversations": st.session_state.conversations,
        "current_conversation_id": st.session_state.current_conversation_id,
        "next_conversation_id": st.session_state.next_conversation_id
    })
    st.rerun()
