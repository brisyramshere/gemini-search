import sys
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import asyncio
import re

# 将src目录添加到Python路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ai_core import get_ai_response_stream, generate_research_report_stream
from src.config import init_config, get_config
from src.utils import preprocess_history_for_report

# --- 全局变量 ---
console = Console()
SEARCH_MODEL_FOR_TEST = "models/gemini-2.0-flash-001" 
REPORT_MODEL_FOR_TEST = "models/gemini-2.5-pro"

async def run_chat_turn(prompt, history):
    """运行一轮聊天对话并返回最终结果。"""
    console.print(f"[bold green]You:[/bold green] {prompt}")
    console.print("\n[bold blue]Assistant:[/bold blue] ", end="")
    
    full_response = ""
    
    response_stream = get_ai_response_stream(prompt, model_name=SEARCH_MODEL_FOR_TEST, history=history)
    
    for event in response_stream:
        if event["type"] == "tool_code":
            console.print(f"\n[yellow]🔍 正在搜索: `{event['query']}`[/yellow]")
        elif event["type"] == "text_chunk":
            print(event["chunk"], end="", flush=True)
            full_response += event["chunk"]
        elif event["type"] == "final_response":
            print()
        elif event["type"] == "error":
            console.print(f"\n[bold red]错误:[/bold red] {event['message']}")
            full_response = event["message"]
            break
            
    console.print("-" * 50)
    return {"role": "assistant", "content": full_response, "type": "chat"}

async def run_report_generation(history):
    """运行报告生成并打印结果，现在会自己附加引用列表。"""
    console.print(Panel("[bold cyan]🚀 开始生成研究报告...[/bold cyan]", expand=False))

    # --- 调试步骤：在调用AI之前，先检查预处理函数的输出 ---
    console.print("\n[bold yellow]----------- DEBUG: Inspecting pre-processing output -----------[/bold yellow]")
    processed_text, global_refs = preprocess_history_for_report(history)
    console.print(f"Type of global_refs: {type(global_refs)}")
    console.print(f"Length of global_refs: {len(global_refs)}")
    console.print(f"Content of global_refs:\n---\n{global_refs}\n---")
    console.print("[bold yellow]-------------------- END OF DEBUG --------------------[/bold yellow]\n")


    console.print("\n[bold magenta]报告生成中:[/bold magenta] ", end="")
    report_body = ""
    final_references = ""
    
    # 调用已经更新的报告生成流
    response_stream = generate_research_report_stream(history, model_name=REPORT_MODEL_FOR_TEST)
    
    for event in response_stream:
        if event["type"] == "report_chunk":
            print(event["chunk"], end="", flush=True)
            report_body += event["chunk"]
        elif event["type"] == "final_references":
            # 收到由代码生成的、100%准确的引用列表
            final_references = event["content"]
        elif event["type"] == "final_response":
            print() # 换行
        elif event["type"] == "error":
            console.print(f"\n[bold red]错误:[/bold red] {event['message']}")
            report_body = event["message"]
            break
            
    # 将报告正文和准确的引用列表拼接起来
    full_report = report_body
    if final_references:
        # 移除可能由模型意外生成的引用标题
        report_body = re.sub(r"(?i)(?:\*\*References:|参考文献:)\s*$", "", report_body.strip())
        full_report = report_body + "\n\n## References\n" + final_references

    console.print(Panel("[bold green]✅ 报告生成完毕[/bold green]", expand=False))
    console.print(Markdown(full_report))
    console.print("-" * 50)


async def main_console_app():
    """
    一个用于测试最终优化方案的终端应用。
    """
    init_config()
    
    console.print(Markdown("# 🤖 Gemini 引用排序功能测试 (最终版)"))
    console.print(f"搜索模型: [cyan]{SEARCH_MODEL_FOR_TEST}[/cyan] | 报告模型: [cyan]{REPORT_MODEL_FOR_TEST}[/cyan]")
    console.print("-" * 50)

    if not get_config("api_key"):
        console.print("[bold red]错误: 未找到 Gemini API Key。[/bold red]")
        return

    history = []

    # --- 对话轮次 ---
    prompts = [
        "神经内镜有哪些主流的厂商？",
        "神经内镜有什么用？"
    ]
    for prompt in prompts:
        assistant_response = await run_chat_turn(prompt, history)
        history.append({"role": "user", "content": prompt, "type": "chat"})
        history.append(assistant_response)
    
    # --- 生成报告 ---
    await run_report_generation(history)


if __name__ == "__main__":
    try:
        import rich
    except ImportError:
        print("Rich 库未安装。请运行: pip install rich")
        sys.exit(1)
        
    asyncio.run(main_console_app())