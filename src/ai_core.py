import google.genai as genai
from google.genai import types
import re

from src.config import load_api_key, get_config
from src.utils import preprocess_history_for_report # 导入新的预处理函数

def _get_client():
    """Helper to initialize and return the genai.Client"""
    api_key = load_api_key()
    # The base_url is now fetched dynamically via get_config
    base_url = get_config("api_endpoint")
    http_options = {"base_url": base_url} if base_url else None
    return genai.Client(api_key=api_key, http_options=http_options)

def _process_response_stream(response_stream):
    """Processes the stream and yields events."""
    for chunk in response_stream:
        # Process tool calls (search queries)
        if (chunk.candidates and chunk.candidates[0].content.parts and
            chunk.candidates[0].content.parts[0].function_call):
            function_call = chunk.candidates[0].content.parts[0].function_call
            if isinstance(function_call.args, dict) and 'query' in function_call.args:
                yield {"type": "tool_code", "query": str(function_call.args['query'])}

        # Process text chunks
        if chunk.text:
            yield {"type": "text_chunk", "chunk": chunk.text}

    # After the stream is finished, yield a final response marker.
    yield {"type": "final_response"}

def get_ai_response_stream(prompt: str, model_name: str, history: list = None):
    """Gets a streamed response for a standard chat query."""
    try:
        client = _get_client()
        search_tool = types.Tool(google_search=types.GoogleSearch())
        # Dynamically load the system prompt each time
        system_prompt = get_config("system_prompt")
        config = types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=system_prompt
        )

        contents = []
        if history:
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": item["content"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )
        yield from _process_response_stream(response_stream)

    except Exception as e:
        yield {"type": "error", "message": f"An error occurred: {e}"}

def generate_research_report_stream(history: list, model_name: str):
    """
    Generates a research report stream. The model generates the body,
    and this function appends the pre-processed, accurate reference list.
    """
    try:
        client = _get_client()
        # 1. Filter for actual chat messages
        chat_history = [msg for msg in history if msg.get("type") == "chat"]
        if not chat_history:
            yield {"type": "error", "message": "当��对话没有内容可供生成报告。"}
            return

        # 2. Preprocess history to get cleaned text and the accurate reference list
        processed_history_text, global_references_str = preprocess_history_for_report(chat_history)

        if not processed_history_text:
             yield {"type": "error", "message": "预处理后没有内容可供生成报告。"}
             return

        # 3. Dynamically load the report prompt template
        report_prompt_template = get_config("report_prompt")
        
        # 4. Construct the final prompt, now instructing the model NOT to generate a reference list.
        final_prompt = (
            f"{report_prompt_template}\n\n"
            f"**CRITICAL INSTRUCTION: Your task is to synthesize the 'Conversation History' into a report. "
            f"You MUST correctly use the citation markers (e.g., [^1], [^2]) as they appear in the text. "
            f"DO NOT generate a 'References' or '参考文献' section at the end of your report. This will be handled externally.**\n\n"
            f"**Conversation History to Synthesize:**\n---\n"
            f"{processed_history_text}\n---"
        )
        
        # 5. Call the Gemini API
        config = types.GenerateContentConfig()
        contents = [{"role": "user", "parts": [{"text": final_prompt}]}]

        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        # 6. Yield the report body chunks from the model
        for chunk in response_stream:
            if chunk.text:
                yield {"type": "report_chunk", "chunk": chunk.text}

        # 7. After the model is done, yield the accurate, pre-processed reference list
        # This ensures the reference list is always 100% correct.
        if global_references_str:
            yield {"type": "final_references", "content": global_references_str}
        
        # Yield a final response marker to signal completion.
        yield {"type": "final_response"}

    except Exception as e:
        yield {"type": "error", "message": f"调用 Gemini API 生成报告时出错: {e}"}

