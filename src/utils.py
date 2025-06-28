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

def correct_references(text: str, citations: list) -> str:
    """
    使用从API获取的准确引用数据，查找并替换模型生成的Markdown文本中的链接，
    确保它们是标准的、可点击的Markdown链接。
    """
    if not citations:
        return text

    # 创建一个从标题到URL的映射，方便查找
    # ��们将标题转换为小写并移除空格，以便进行更宽松的匹配
    title_to_url = {re.sub(r'\s+', '', item['title'].lower()): item['url'] for item in citations}

    # 正则表达式，用于匹配有序列表项，例如：`1. [Some Title](some_url)`
    # 它会捕获列表编号(number)和链接文本(title)
    markdown_list_pattern = re.compile(r'(\d+\.\s*\[)([^\]]+)(\]\([^\)]*\))')

    def replace_link(match):
        # 从匹配中获取列表编号和标题
        list_prefix, title, link_suffix = match.groups()
        
        # 规范化标题以进行查找
        normalized_title = re.sub(r'\s+', '', title.lower())
        
        # 在我们的准确引用列表中查找这个标题
        correct_url = title_to_url.get(normalized_title)
        
        # 如果找到了对应的标题，就构建一个语法完全正确的Markdown链接
        if correct_url:
            return f"{list_prefix}{title}]({correct_url})"
        else:
            # 如果没找到，就保留模型原来的输出
            return match.group(0)

    # 在整个文本中执行查找和替换
    corrected_text = markdown_list_pattern.sub(replace_link, text)
    
    return corrected_text