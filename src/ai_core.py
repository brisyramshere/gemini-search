import google.genai as genai
from google.genai import types
import re

from src.config import load_api_key, load_base_url

# --- 常规对话的系统提示词 ---
CHAT_SYSTEM_PROMPT = (
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

# --- 研究报告生成的系统提示词 (简化版) ---
REPORT_SYSTEM_PROMPT = (
    "You are a professional researcher and analyst.\n"
    "Your task is to synthesize the provided conversation history into a comprehensive and well-structured research report.\n"
    "The conversation history contains user questions, AI answers, and citation markers (e.g., [^1], [^2]).\n\n"
    "**Your task is to act as a summarizer and organizer, not a new researcher.**\n"
    "**DO NOT perform any new web searches.** Base your report EXCLUSIVELY on the information and sources already present in the conversation history.\n\n"
    "Follow these steps:\n"
    "1. **Review and Synthesize**: Thoroughly review the entire conversation history to understand the key topics, findings, and all cited sources.\n"
    "2. **Structure and Write**: Draft a formal report in Markdown format with a clear structure, including an introduction, key findings, detailed analysis, and a conclusion. \n"
    "3. **Cite Everything**: CRITICALLY, every piece of information in your report must be accurately cited. Use the citation markers `[^N]` exactly as they appear in the original conversation. All citations must be consolidated and listed at the end of the report under a 'References' section.\n"
    "4. **Demarcate the Report**: Start the actual report with a `---` separator. Before the separator, you can briefly outline your plan, but after the separator, only the report content should exist."
)

def _get_client():
    """Helper to initialize and return the genai.Client"""
    api_key = load_api_key()
    base_url = load_base_url()
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
        config = types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=CHAT_SYSTEM_PROMPT
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


def generate_research_report_stream(history: list, model_name: str = "models/gemini-2.5-pro"):
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

        # 2. Create the Meta-Prompt for the report.
        report_prompt = f"""
请你扮演一个专业的研究助理，你的任务是根据下面提供的对话历史，撰写一份结构化的研究报告。

**报告要求:**
1.  **综合分析**: 全面综合对话中的所有问题、回答、以及搜索到的信息。
2.  **结构清晰**: 报告必须包含明确的标题、摘要、引言、正文（可分章节）、以及结论。
3.  **提取并格式化参考文献**:
    - 在报告的末尾创建一个名为“**参考文献**”的独立章节。
    - 从对话历史中，识��出所有由AI助手提供的、格式为 `[标题](URL)` 的Markdown链接。
    - 将这些链接以带编号的列表形式，清晰地罗列在“参考文献”章节中。
4.  **正文引用**:
    - 在报告正文中，如果内容引用自某个参考文献，请使用方括号加数字（如 `[1]`, `[2]`）的方式进行标注。
    - 引用编号必须与“参考文献”列表中的编号一一对应。
5.  **语言一致**: 报告的语言（例如，中文或英文）应与对话历史中使用的主要语言保持一致。
6.  **格式**: 全文使用 Markdown 格式。

**以下是需要分析的对话历史:**
---
{formatted_history}
---
"""
        # 3. Call the Gemini API using the client
        config = types.GenerateContentConfig(
            # No tools needed for reporting, it only synthesizes.
            system_instruction=REPORT_SYSTEM_PROMPT 
        )
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
