import streamlit as st
import re
from src.ai_core import get_ai_response_stream, generate_research_report_stream
from src.utils import save_conversations_to_file, load_conversations_from_file
from src.config import init_config, get_config, update_config, save_config

# --- 页面配置 ---
st.set_page_config(
    page_title="Gemini 联网搜索聊天",
    page_icon="🤖",
    layout="wide",
)

# --- 初始化配置 ---
init_config()

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

# --- 函数定义 ---
def create_new_conversation():
    """创建一个新的对话。"""
    new_id = str(st.session_state.next_conversation_id)
    st.session_state.conversations[new_id] = {
        "title": f"新对话 {new_id}",
        "messages": [{"role": "assistant", "content": "你好！我可以联网查询最新信息，并告诉你我的信息来源。", "type": "chat"}]
    }
    st.session_state.current_conversation_id = new_id
    st.session_state.next_conversation_id += 1
    save_conversations_to_file({
        "conversations": st.session_state.conversations,
        "current_conversation_id": st.session_state.current_conversation_id,
        "next_conversation_id": st.session_state.next_conversation_id
    })
    st.rerun()

# --- 侧边栏 ---
with st.sidebar:
    st.header("Gemini 搜索")

    # --- 对话管理与设置 ---
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        if st.button("➕ 新对话", use_container_width=True):
            create_new_conversation()
    with col2:
        settings_popover = st.popover("⚙", use_container_width=True)

    with settings_popover:
        with st.form("settings_form"):
            st.subheader("API 配置")
            api_endpoint = st.text_input("API Endpoint", value=get_config("api_endpoint"))
            api_key = st.text_input("Gemini API Key", type="password", value=get_config("api_key"))

            st.subheader("模型选择")
            model_options = ["models/gemini-2.5-pro", "models/gemini-2.5-flash", "models/gemini-2.0-flash-001"]
            search_model = st.selectbox(
                "搜索模型",
                options=model_options,
                index=model_options.index(get_config("search_model", "models/gemini-2.5-flash"))
            )
            report_model = st.selectbox(
                "报告生成模型",
                options=model_options,
                index=model_options.index(get_config("report_model", "models/gemini-2.5-pro"))
            )

            st.subheader("提示词 (Prompts)")
            system_prompt = st.text_area("系统提示词", value=get_config("system_prompt"), height=200)
            report_prompt = st.text_area("报告生成提示词", value=get_config("report_prompt"), height=200)

            submitted = st.form_submit_button("保存设置")
            if submitted:
                update_config("api_endpoint", api_endpoint)
                update_config("api_key", api_key)
                update_config("search_model", search_model)
                update_config("report_model", report_model)
                update_config("system_prompt", system_prompt)
                update_config("report_prompt", report_prompt)
                st.toast("设置已保存！")
                # Popover will close automatically on rerun, no need for .close()
                st.rerun()
    
    st.header("历史对话")

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
    st.info("点击“生成调研报告”按钮，可将当前对话内容合成为一份研究报告。")

# --- 获取当前对话 ---
current_conversation = st.session_state.conversations[st.session_state.current_conversation_id]

# --- 页面标题 ---
st.title("🤖 Gemini 联网搜索聊天")
st.header(f"{current_conversation['title']}")
st.caption(f"一个能展示思考过程并引用来源的AI聊天机器人 (搜索模型: {get_config('search_model')})")

# --- 显示历史消息 ---
for i, message in enumerate(current_conversation["messages"]):
    with st.chat_message(message["role"]):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(message["content"])
            
            # 如果消息是报告并且有引用，则在折叠控件中显示它们
            if message.get("type") == "report" and "references" in message and message["references"]:
                with st.expander("参考文献"):
                    st.markdown(message["references"])

            if message["role"] == "assistant" and "model" in message:
                st.caption(f"由 {message['model']} 生成")
        with col2:
            if st.button("🗑️", key=f"msg_delete_{st.session_state.current_conversation_id}_{i}", use_container_width=True):
                del current_conversation["messages"][i]
                save_conversations_to_file({
                    "conversations": st.session_state.conversations,
                    "current_conversation_id": st.session_state.current_conversation_id,
                    "next_conversation_id": st.session_state.next_conversation_id
                })
                st.rerun()


# --- 报告生成处理 ---
if st.session_state.get("generating_report"):
    st.session_state.generating_report = False
    with st.chat_message("assistant"):
        report_placeholder = st.empty()
        report_model_name = get_config("report_model")
        report_body = ""
        final_references = ""

        try:
            history = current_conversation["messages"]
            response_stream = generate_research_report_stream(history, model_name=report_model_name)
            
            for event in response_stream:
                if event["type"] == "report_chunk":
                    report_body += event["chunk"]
                    report_placeholder.markdown(report_body + "▌")
                elif event["type"] == "final_references":
                    final_references = event["content"]
                elif event["type"] == "error":
                    st.error(event["message"])
                    report_body = event["message"]
                    break
            
            # 清理可能由模型意外生成的引用标题
            cleaned_body = re.sub(r"(?i)\s*(#+\s*References|#+\s*参考文献)\s*$", "", report_body.strip())
            
            # 在UI上显示最终的报告正文
            report_placeholder.markdown(cleaned_body)

            # 在独立的折叠控件中显示引用
            if final_references:
                with st.expander("参考文献"):
                    st.markdown(final_references)

        except Exception as e:
            st.error(f"生成报告时出现严重错误: {e}")
            cleaned_body = "生成报告时出现严重错误，请检查后台日志。"
            report_placeholder.markdown(cleaned_body)

    # 将结构化的报告（正文和引用分离）保存到对话历史
    if cleaned_body or final_references:
        current_conversation["messages"].append({
            "role": "assistant", 
            "content": cleaned_body, 
            "references": final_references,
            "type": "report", 
            "model": report_model_name
        })
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
        # 检查 API Key 是否已设置
        if not get_config("api_key"):
            st.error("请先在侧边栏的“设置”中输入您的 Gemini API Key。")
        else:
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
    # 检查 API Key 是否已设置
    if not get_config("api_key"):
        st.error("请先在侧边栏的“设置”中输入您的 Gemini API Key。")
    else:
        current_conversation["messages"].append({"role": "user", "content": prompt, "type": "chat"})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full_response = ""
            response_placeholder = st.empty()
            search_model_name = get_config("search_model") # 获取模型名称
            
            history = current_conversation["messages"][:-1]

            try:
                # 使用配置中的搜索模型
                response_stream = get_ai_response_stream(prompt, model_name=search_model_name, history=history)
                
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

        current_conversation["messages"].append({"role": "assistant", "content": full_response, "type": "chat", "model": search_model_name})

        if len(current_conversation["messages"]) <= 3:
            current_conversation["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")
        
        save_conversations_to_file({
            "conversations": st.session_state.conversations,
            "current_conversation_id": st.session_state.current_conversation_id,
            "next_conversation_id": st.session_state.next_conversation_id
        })
        st.rerun()

