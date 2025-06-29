import google.genai as genai
from google.genai import types
import re

from src.config import load_api_key, get_config

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

def _format_history_for_report(history: list) -> str:
    """Formats the conversation history for the report generation prompt."""
    formatted_string = ""
    for message in history:
        # Ensure the message has the expected keys
        if "role" in message and "content" in message:
            role = "User" if message["role"] == "user" else "Assistant"
            content = message["content"]
            formatted_string += f"**{role}:**\n{content}\n\n---\n"
    return formatted_string.strip()


def generate_research_report_stream(history: list, model_name: str):
    """
    Generates a research report stream based on the conversation history by calling the Gemini API.
    """
    try:
        client = _get_client()
        # 1. Filter for actual chat messages to build the report from.
        chat_history = [msg for msg in history if msg.get("type") == "chat"]
        if not chat_history:
            yield {"type": "error", "message": "当前对话没有内容可供生成报告。"}
            return

        formatted_history = _format_history_for_report(chat_history)

        # 2. Dynamically load the report prompt each time.
        report_prompt_template = get_config("report_prompt")
        report_prompt = f"{report_prompt_template}\n\n**以下是需要分析的对话历史:**\n---\n{formatted_history}\n---"

        # 3. Call the Gemini API using the client
        # No system instruction needed as the full instruction is in the user prompt
        config = types.GenerateContentConfig()
        contents = [{"role": "user", "parts": [{"text": report_prompt}]}]

        response_stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        # 4. Yield the response chunks
        for chunk in response_stream:
            if chunk.text:
                yield {"type": "report_chunk", "chunk": chunk.text}

        # Yield a final response marker to signal completion.
        yield {"type": "final_response"}

    except Exception as e:
        yield {"type": "error", "message": f"调用 Gemini API 生成报告时出错: {e}"}