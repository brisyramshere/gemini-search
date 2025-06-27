import google.genai as genai
from google.genai import types

from src.config import load_api_key

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

def get_ai_response_stream(prompt: str, model_name: str = "models/gemini-1.5-pro-latest"):
    """
    以流的形式获取AI的响应，生成用于显示思考过程和最终结果的事件。
    严格遵循 google-genai SDK 的官方用法。
    """
    try:
        api_key = load_api_key()
        
        # 1. 使用 Client 类进行初始化
        client = genai.Client(api_key=api_key)

        # 2. 定义搜索工具
        search_tool = types.Tool(google_search=types.GoogleSearch())

        # 3. 定义配置，将系统提示词放在 system_instruction 中
        config = types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=SYSTEM_PROMPT
        )

        # 4. 构造请求内容，直接传递字符串即可
        contents = prompt

        # 5. 调用 generate_content_stream 并处理流
        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        final_response = None
        for chunk in response_stream:
            # 检查并生成��具调用（搜索）事件
            if (
                chunk.candidates and chunk.candidates[0].content.parts
                and chunk.candidates[0].content.parts[0].function_call
            ):
                query = chunk.candidates[0].content.parts[0].function_call.args.get('query')
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