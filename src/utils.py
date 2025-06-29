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

