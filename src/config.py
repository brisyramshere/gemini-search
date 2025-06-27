import os
from dotenv import load_dotenv

def load_api_key():
    """
    从 .env 文件加载 Google API 密钥。

    Raises:
        ValueError: 如果 GOOGLE_API_KEY 未设置。

    Returns:
        str: Google API 密钥。
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    return api_key

def load_base_url():
    """
    从 .env 文件加载可选的 API base URL。

    Returns:
        str or None: 如果设置了，则返回 base URL，否则返回 None。
    """
    load_dotenv()
    return os.getenv("API_BASE_URL")