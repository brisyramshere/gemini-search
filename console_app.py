import sys
import os
from rich.console import Console
from rich.markdown import Markdown

# 将src目录添加到Python路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ai_core import get_ai_response_stream
from src.utils import correct_references

def main_console_app():
    """
    一个功能与Streamlit应用对等的纯终端聊天应用，用于调试。
    移除了交互式输入，并使用一个需要联网搜索的问题来测试特定模型的功能。
    """
    console = Console()
    
    console.print(Markdown("# 🤖 Gemini 联网搜索聊天 (终端版)"))
    console.print("这是一个用于调试的纯终端聊天机器人。")
    console.print("-" * 50)

    # --- 模型选择 (硬编码用于非交互式测试) ---
    selected_model = "models/gemini-2.5-flash"
    console.print(f"正在测试模型: [cyan]{selected_model}[/cyan]")
    console.print("-" * 50)

    # --- 聊天循环 (修改为单次执行，使用需要联网搜索的问题) ---
    try:
        prompt = "英伟达（NVIDIA）今天的股价是多少？"
        console.print(f"[bold green]You:[/bold green] {prompt}")

        console.print("\n[bold blue]Assistant:[/bold blue] ", end="")
        
        full_response = ""
        citations_from_api = []
        
        # 调用核心AI逻辑
        response_stream = get_ai_response_stream(prompt, model_name=selected_model)
        
        for event in response_stream:
            if event["type"] == "tool_call":
                console.print(f"\n[yellow]🔍 正在搜索: `{event['query']}`[/yellow]")
            
            elif event["type"] == "text_chunk":
                # 实时打印文本块
                print(event["chunk"], end="", flush=True)
                full_response += event["chunk"]
            
            elif event["type"] == "final_response":
                citations_from_api = event.get("citations", [])
                # 最终响应处理前，换个行
                print() 
            
            elif event["type"] == "error":
                console.print(f"\n[bold red]错误:[/bold red] {event['message']}")
                full_response = event["message"]
                break
        
        # 修正引用并用Markdown格式打印最终结果
        final_corrected_text = correct_references(full_response, citations_from_api)
        console.print("\n" + "-"*20 + " [Final Response] " + "-"*20)
        console.print(Markdown(final_corrected_text))
        console.print("-" * 50 + "\n")

    except Exception as e:
        console.print(f"\n[bold red]应用出现严重错误:[/bold red] {e}")

if __name__ == "__main__":
    # 为了让rich库正常工作，可能需要安装它
    try:
        import rich
    except ImportError:
        print("Rich 库未安装。请运行: pip install rich")
        sys.exit(1)
        
    main_console_app()