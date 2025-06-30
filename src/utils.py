import re
import json
import os

CONVERSATIONS_FILE = "conversations.json"

def save_conversations_to_file(conversations_data):
    """将对话数据保存到JSON文件。"""
    try:
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(conversations_data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving conversations to file: {e}")

def load_conversations_from_file():
    """从JSON文件加载对话数据。"""
    if not os.path.exists(CONVERSATIONS_FILE):
        return None
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading conversations from file: {e}")
        return None

def preprocess_history_for_report(history: list):
    """
    预处理对话历史，提取、去重并重新编号所有参考文献，确保内容和格式正确。
    """
    from collections import OrderedDict
    global_references = OrderedDict()
    
    # 经过验证的、能准确匹配 [^N]: [Title](URL) 格式的正则表达式
    ref_regex = r'\[\^(\d+)\]:\s*\[([^\]]+)\]\(([^)]+)\)'

    # 1. 遍历所有助手消息，提取所有引用
    for message in history:
        if message.get("role") == "assistant" and "content" in message:
            found = re.findall(ref_regex, message["content"])
            for _, title, url in found:
                if url not in global_references:
                    global_references[url] = title

    if not global_references:
        # 如果没有找到任何引用，直接拼接历史记录返回
        full_text = ""
        for msg in history:
            if msg.get("role") and msg.get("content"):
                 full_text += f"**{msg['role'].capitalize()}**: {msg['content']}\n\n---\n"
        return full_text, ""

    # 2. 创建全局 URL 到新索引的映射
    url_to_new_index = {url: i + 1 for i, url in enumerate(global_references.keys())}

    # 3. 构建最终的、格式正确的全局 Markdown 引用字符串
    global_references_str = ""
    for url, index in url_to_new_index.items():
        title = global_references[url]
        global_references_str += f"{index}. [{title}]({url})\n"

    # 4. 重写消息内容
    processed_messages_text = ""
    for message in history:
        role = message.get("role")
        content = message.get("content")
        
        if not role or not content:
            continue

        processed_messages_text += f"**{role.capitalize()}**: "
        
        if role == "assistant":
            # 提取当前消息的局部引用
            local_refs_found = re.findall(ref_regex, content)
            local_index_to_url = {int(index): url for index, _, url in local_refs_found}
            
            # 移除所有引用定义行，得到干净的正文
            content_body = re.sub(ref_regex, '', content).strip()

            # 定义替换函数
            def replace_marker(match):
                local_index = int(match.group(1))
                url = local_index_to_url.get(local_index)
                if url:
                    new_index = url_to_new_index.get(url)
                    if new_index:
                        return f"[^{new_index}]"
                return match.group(0)

            # 只替换正文中的引用标记，如 [^1]，而不是引用定义 [^1]:
            content_body = re.sub(r'\[\^(\d+)\](?!:)', replace_marker, content_body)
            processed_messages_text += content_body
        else:
            processed_messages_text += content

        processed_messages_text += "\n\n---\n"

    return processed_messages_text.strip(), global_references_str.strip()

