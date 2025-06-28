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
        # 硬编码的对话历史
        history = [
            {"role": "user", "content": "你好，我正在了解人工智能领域。"},
            {"role": "assistant", "content": "你好！人工智能是一个非常广泛且有趣的领域。你想了解哪个具体方面呢？比如机器学习、自然语言处理，还是计算机视觉？"},
            {"role": "user", "content": "我对自然语言处理（NLP）比较感兴趣，尤其是大型语言模型。你能简单介绍一下它的发展历史吗？"},
            {"role": "assistant", "content": "当然。大型语言模型（LLM）的发展大致可以分为几个阶段。早期是基于规则和统计的模型，如N-gram。接着是循环神经网络（RNN）和长短期记忆网络（LSTM）的出现，它们能更好地处理序列数据。近年来，基于Transformer架构的模型，如BERT和GPT系列，取得了突破性进展，它们通过自注意力机制（Self-Attention）极大地提升了性能，成为了当前的主流。"},
        ]
        
        # 打印历史消息
        console.print("[bold]聊天记录:[/bold]")
        for message in history:
            color = "green" if message["role"] == "user" else "blue"
            console.print(f"[bold {color}]{message['role'].capitalize()}:[/bold {color}] {message['content']}")
        console.print("-" * 50)

        prompt = "基于我们上面的讨论，请问现在最领先的几个模型是哪些，它们各有什么特点？"
        console.print(f"[bold green]You:[/bold green] {prompt}")

        console.print("\n[bold blue]Assistant:[/bold blue] ", end="")
        
        full_response = ""
        citations_from_api = []
        
        # 调用核心AI逻辑，并传入历史记录
        response_stream = get_ai_response_stream(prompt, model_name=selected_model, history=history)
        
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