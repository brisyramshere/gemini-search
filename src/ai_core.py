import google.genai as genai
from google.genai import types

from src.config import load_api_key, load_base_url

# 系统提示词，指导模型如何回答和引用
SYSTEM_PROMPT = (
    "You are a helpful and informative AI assistant that provides answers grounded in web search results.\n"
    "When you answer, you MUST cite your sources.\n"
    "For each piece of information you provide, add a citation marker in the format [^N] where N is the number of the source.\n"
    "At the end of your entire response, provide a 'References:' section.\n"
    "Under the 'References:' section, list all the sources you used as a standard Markdown numbered list.\n"
    "Each item in the list should be in the format: `1. [Source Title](URL)`.\n\n"
    "Example:\n"
    "The sky is blue due to a phenomenon called Rayleigh scattering [^1].\n\n"
    "References:\n"
    "1. [What Makes the Sky Blue?](https://www.space.com/what-makes-the-sky-blue)"
)

def get_ai_response_stream(prompt: str, model_name: str = "models/gemini-1.5-pro-latest", history: list = None):
    """
    以流的形式获取AI的响应，生成用于显示思考过程和最终结果的事件。
    严格遵循 google-genai SDK 的官方用法。
    """
    try:
        api_key = load_api_key()
        base_url = load_base_url()

        # 1. 准备 http_options（如果 base_url 存在）
        http_options = {}
        if base_url:
            http_options["base_url"] = base_url
        
        # 2. 使用 Client 类进行初始化
        client = genai.Client(api_key=api_key, http_options=http_options if http_options else None)

        # 3. 定义搜索工具
        search_tool = types.Tool(google_search=types.GoogleSearch())

        # 4. 定义配置，将系统提示词放在 system_instruction 中
        config = types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=SYSTEM_PROMPT
        )

        # 5. 构造请求内容，包含历史记录和当前问题
        contents = []
        if history:
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": item["content"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})


        # 6. 调用 generate_content_stream 并处理流
        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        final_response = None
        for chunk in response_stream:
            # 检查并生成工具调用（搜索）事件
            if (
                chunk.candidates and chunk.candidates[0].content.parts
                and chunk.candidates[0].content.parts[0].function_call
            ):
                function_call = chunk.candidates[0].content.parts[0].function_call
                args = function_call.args
                query = None

                # 代理可能会将 args 作为列表返回，而不是字典，我们需要更灵活地处理
                if isinstance(args, dict):
                    query = args.get('query')
                elif isinstance(args, list) and len(args) > 0:
                    # 有时它是一个包含字典的列表
                    if isinstance(args[0], dict):
                        query = args[0].get('query')
                    # 有时它直接就是一个字符串列表
                    elif isinstance(args[0], str):
                        query = args[0]
                
                if query:
                    yield {"type": "tool_call", "query": str(query)}
            
            # 生成文本块事件
            if chunk.text:
                yield {"type": "text_chunk", "chunk": chunk.text}
            
            # 保存最后一块响应，用于提取最终的引用
            final_response = chunk

        # 流结束后，从最后一块响应中提取引用信息
        citations = []
        if final_response and final_response.candidates and final_response.candidates[0].grounding_metadata:
            metadata = final_response.candidates[0].grounding_metadata
            if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
                 for support in metadata.grounding_supports:
                    if hasattr(support, 'web') and support.web:
                        citations.append({
                            "title": support.web.title,
                            "url": support.web.uri
                        })
            # 有时引用信息在 aattributions 中
            elif hasattr(metadata, 'attributions') and metadata.attributions:
                 for attribution in metadata.attributions:
                     if hasattr(attribution, 'web') and attribution.web:
                        citations.append({
                            "title": attribution.web.title,
                            "url": attribution.web.uri
                        })

        yield {"type": "final_response", "citations": citations}

    except Exception as e:
        print(f"Error generating content: {e}")
        yield {"type": "error", "message": f"抱歉，处理时出现错误: {e}"}
