import streamlit as st
import re
from src.ai_core import get_ai_response_stream, generate_research_report_stream
from src.utils import save_conversations_to_file, load_conversations_from_file

# --- 页面配置 ---
st.set_page_config(
    page_title="Gemini 联网搜索聊天",
    page_icon="🤖",
    layout="wide",
)

# --- 会话状态初始化 ---
if "conversations" not in st.session_state:
    conversations_data = load_conversations_from_file()
    if conversations_data:
        st.session_state.conversations = conversations_data.get("conversations", {})
        st.session_state.current_conversation_id = conversations_data.get("current_conversation_id", "1")
        st.session_state.next_conversation_id = conversations_data.get("next_conversation_id", 2)
    else:
        st.session_state.conversations = {
            "1": {"title": "新对话 1", "messages": [{"role": "assistant", "content": "你好！我可以联网查询最新信息，并告诉你我的信息来源。", "type": "chat"}]}
        }
        st.session_state.current_conversation_id = "1"
        st.session_state.next_conversation_id = 2
    save_conversations_to_file({
        "conversations": st.session_state.conversations,
        "current_conversation_id": st.session_state.current_conversation_id,
        "next_conversation_id": st.session_state.next_conversation_id
    })

if "generating_report" not in st.session_state:
    st.session_state.generating_report = False

# --- 侧边栏 ---
with st.sidebar:
    st.header("模型配置")
    model_options = {
        "Gemini 2.5 Pro (推荐)": "models/gemini-2.5-pro",
        "Gemini 2.5 Flash": "models/gemini-2.5-flash",
        "Gemini 2.0 Flash": "models/gemini-2.0-flash-001",
    }
    
    selected_model_key = st.selectbox(
        "选择一个 Gemini 模型:",
        options=list(model_options.keys()),
        index=list(model_options.values()).index(st.session_state.get("selected_model", "models/gemini-2.5-pro"))
    )
    st.session_state.selected_model = model_options[selected_model_key]

    st.markdown("---")

    st.header("对话管理")

    def create_new_conversation():
        conv_id = str(st.session_state.next_conversation_id)
        st.session_state.conversations[conv_id] = {
            "title": f"新对话 {conv_id}",
            "messages": [{"role": "assistant", "content": "你好！这是一个新的对话。", "type": "chat"}]
        }
        st.session_state.current_conversation_id = conv_id
        st.session_state.next_conversation_id += 1
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })

    if st.button("➕ 新对话", use_container_width=True):
        create_new_conversation()

    conversation_ids = list(st.session_state.conversations.keys())
    current_id = st.session_state.current_conversation_id
    
    # Ensure current_conversation_id is valid
    if current_id not in conversation_ids:
        current_id = conversation_ids[0] if conversation_ids else "1"
        st.session_state.current_conversation_id = current_id

    # --- 侧边栏对话列表 ---
    for conv_id in conversation_ids:
        with st.container():
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(st.session_state.conversations[conv_id]["title"], key=f"conv_select_{conv_id}", use_container_width=True):
                    st.session_state.current_conversation_id = conv_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"conv_delete_{conv_id}", use_container_width=True):
                    # 删除对话
                    del st.session_state.conversations[conv_id]
                    # 如果删除的是当前对话，则切换到列表中的第一个对话
                    if st.session_state.current_conversation_id == conv_id:
                        if st.session_state.conversations:
                            st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
                        else:
                            # 如果所有对话都被删除了，创建一个新的
                            create_new_conversation()
                    save_conversations_to_file({
                        "conversations": st.session_state.conversations,
                        "current_conversation_id": st.session_state.current_conversation_id,
                        "next_conversation_id": st.session_state.next_conversation_id
                    })
                    st.rerun()

    st.markdown("---")
    st.info("点击“一键生成报告”按钮，可将当前对话内容合成为一份研究报告。")

# --- 获取当前对话 ---
current_conversation = st.session_state.conversations[st.session_state.current_conversation_id]

# --- 页面标题 ---
st.title("🤖 Gemini 联网搜索聊天 (Pro)")
st.header(f"{current_conversation['title']}")
st.caption(f"一个能展示思考过程并引用来源的AI聊天机器人 (当前模型: {selected_model_key})")

# --- 显示历史消息 ---
for i, message in enumerate(current_conversation["messages"]):
    with st.chat_message(message["role"]):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(message["content"])
        with col2:
            if st.button("🗑️", key=f"msg_delete_{st.session_state.current_conversation_id}_{i}", use_container_width=True):
                del current_conversation["messages"][i]
                save_conversations_to_file({
                    "conversations": st.session_state.conversations,
                    "current_conversation_id": st.session_state.current_conversation_id,
                    "next_conversation_id": st.session_state.next_conversation_id
                })
                st.rerun()

        if message.get("type") == "report" and i == len(current_conversation["messages"]) - 1:
            pass


# --- 报告生成处理 ---
if st.session_state.get("generating_report"):
    st.session_state.generating_report = False
    with st.chat_message("assistant"):
        report_placeholder = st.empty()
        report_output = ""

        try:
            history = current_conversation["messages"]
            response_stream = generate_research_report_stream(history, model_name=st.session_state.selected_model)
            
            for event in response_stream:
                if event["type"] == "report_chunk":
                    report_output += event["chunk"]
                    report_placeholder.markdown(report_output + "▌")
                elif event["type"] == "final_response":
                    # The report is complete, finalize the display
                    report_placeholder.markdown(report_output)
                elif event["type"] == "error":
                    st.error(event["message"])
                    report_output = event["message"]
                    break
        except Exception as e:
            st.error(f"生成报告时出现严重错误: {e}")
            report_output = "生成报告时出现严重错误，请检查后台日志。"

    # Add the complete report to the conversation history
    if report_output:
        current_conversation["messages"].append({"role": "assistant", "content": report_output, "type": "report"})
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })
    st.rerun()

# --- 底部功能按钮 ---
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📝 生成调研报告", use_container_width=True):
        st.session_state.generating_report = True
        st.rerun()
with col2:
    # 准备下载内容
    full_conversation_md = f"# {current_conversation['title']}\n\n"
    for msg in current_conversation["messages"]:
        full_conversation_md += f"**{msg['role'].capitalize()}**: \n\n{msg['content']}\n\n---\n\n"
    
    report_title_for_file = re.sub(r'[\\/*?_<>|:]','_', current_conversation['title'])
    st.download_button(
        label="📥 保存为 Markdown",
        data=full_conversation_md,
        file_name=f"对话记录 - {report_title_for_file}.md",
        mime="text/markdown",
        use_container_width=True,
    )

# --- 聊天输入框 ---
if prompt := st.chat_input("请输入您的问题..."):
    current_conversation["messages"].append({"role": "user", "content": prompt, "type": "chat"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ""
        response_placeholder = st.empty()
        
        history = current_conversation["messages"][:-1]

        try:
            response_stream = get_ai_response_stream(prompt, model_name=st.session_state.selected_model, history=history)
            
            for event in response_stream:
                if event["type"] == "tool_code":
                    st.info(f"🔍 正在搜索: `{event['query']}`")
                elif event["type"] == "text_chunk":
                    full_response += event["chunk"]
                    response_placeholder.markdown(full_response + "▌")
                elif event["type"] == "final_response":
                    # The stream is complete, finalize the display
                    response_placeholder.markdown(full_response)
                elif event["type"] == "error":
                    st.error(event["message"])
                    full_response = event["message"]
                    break
            
        except Exception as e:
            st.error(f"应用出现严重错误: {e}")
            full_response = "应用出现严重错误，请检查后台日志。"

    current_conversation["messages"].append({"role": "assistant", "content": full_response, "type": "chat"})

    if len(current_conversation["messages"]) <= 3:
        current_conversation["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")
    
    save_conversations_to_file({
        "conversations": st.session_state.conversations,
        "current_conversation_id": st.session_state.current_conversation_id,
        "next_conversation_id": st.session_state.next_conversation_id
    })
    st.rerun()
