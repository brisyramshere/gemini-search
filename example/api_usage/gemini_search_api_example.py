

import google.genai as genai
from google.genai import types
import json
import os

# 这是一个独立的调试脚本，用于隔离和测试 google-genai API 的行为。

# --- 配置加载 --
# 我们直接从环境变量加载，以保持脚本的独立性。
# 运行前，请确保 .env 文件中的 GOOGLE_API_KEY 已被加载到环境中。
# 例如: source .env
API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = os.getenv("API_BASE_URL") # 可选

# --- 系统提示词 (与主应用保持一致) ---
SYSTEM_PROMPT = (
    "You are a helpful and informative AI assistant that provides answers grounded in web search results.\n"
    "When you answer, you MUST cite your sources.\n"
    "For each piece of information you provide, add a citation marker in the format [^N] where N is the number of the source.\n"
    "At the end of your entire response, provide a 'References:' section.\n"
    "Under the 'References:' section, list all the sources you used as a standard Markdown numbered list.\n"
    "Each item in the list should be in the format: `1. [Source Title](URL)`."
)

def main():
    """
    主函数，执行API调用和调试输出。
    """
    if not API_KEY:
        print("错误：GOOGLE_API_KEY 环境变量未设置。")
        print("请在运行此脚本前执行: export $(cat .env | xargs)")
        return

    print("--- [1] 初始化客户端 ---")
    http_options = {"base_url": BASE_URL} if BASE_URL else None
    client = genai.Client(api_key=API_KEY, http_options=http_options)
    print("客户端初始化成功。")

    # --- [2] 定义请求 ---
    model_name = "models/gemini-2.5-pro"
    # 这个提示强制模型使用搜索
    prompt = "What were the key announcements from the last Google I/O event? Answer with citations."
    
    search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1 # 低温以获得更可复现的结果
    )
    contents = [{"role": "user", "parts": [{"text": prompt}]}]

    print(f"--- [2] 准备调用模型: {model_name} ---")
    print(f"Prompt: {prompt}")

    # --- [3] 执行API调用并详细打印每个块 ---
    try:
        print("\n--- [3] 开始接收流式响应... ---\n")
        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        chunk_count = 0
        for chunk in response_stream:
            chunk_count += 1
            print(f"\n=============== CHUNK {chunk_count} ================")
            
            # 打印原始块，了解其结构
            print("--- RAW CHUNK OBJECT ---")
            print(repr(chunk))
            print("-" * 20)

            # 打印文本内容
            if chunk.text:
                print(f"--- TEXT ---\n{chunk.text}")
            
            # 关键：检查并打印 grounding_metadata
            if hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    metadata = candidate.grounding_metadata
                    if metadata:
                        print("\n*** GROUNDING METADATA FOUND! ***")
                        # 尝试使用 to_dict 或类似的序列化方法
                        try:
                            # 使用 model_dump (如果可用)
                            metadata_dict = metadata.model_dump(exclude_none=True)
                            print(json.dumps(metadata_dict, indent=2))
                        except AttributeError:
                            # 备用方案
                            print(f"Could not serialize metadata object: {repr(metadata)}")
                    else:
                        print("Grounding metadata is present but empty.")
                else:
                    print("(No grounding_metadata attribute in this chunk)")
            
            print("=" * 40)

        print(f"\n--- [4] 流处理完毕，共收到 {chunk_count} 个块。 ---")

    except Exception as e:
        print(f"\n--- !!! API 调用期间发生错误 !!! ---")
        print(e)

if __name__ == "__main__":
    main()
