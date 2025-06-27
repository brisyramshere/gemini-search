import google.generativeai as genai
import os
import traceback
from src.config import load_api_key, load_base_url

def run_tests():
    """
    执行两个独立的API调用测试：一个非流式，一个流式。
    """
    print("--- 开始 API 调用诊断 ---")
    
    # --- 配置加载 ---
    api_key = load_api_key()
    base_url = load_base_url()
    
    if not api_key:
        print("错误: GOOGLE_API_KEY 未找到。")
        return

    client_options = {}
    if base_url:
        client_options = {"api_endpoint": base_url}
        print(f"使用自定义 Base URL: {base_url}")
    else:
        print("使用默认的 Google API URL。")

    genai.configure(api_key=api_key, client_options=client_options)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    prompt = "你好，请只回答“测试成功”。"

    # --- 测试 1: 非流式请求 ---
    print("\n--- [测试 1/2] 正在执行非流式 (Non-Streaming) 请求... ---")
    try:
        response = model.generate_content(prompt)
        print("非流式请求成功！")
        print(f"响应内容: {response.text.strip()}")
    except Exception as e:
        print("非流式请求失败！")
        print(f"捕获到异常: {type(e).__name__} - {e}")
        traceback.print_exc()
        print("由于非流式请求失败，无法继续测试流式请求。请先解决此问题。")
        return # 如果这里失败，后续测试无意义

    # --- 测试 2: 流式请求 ---
    print("\n--- [测试 2/2] 正在执行流式 (Streaming) 请求... ---")
    print("如果程序在此处卡住超过10-20秒，则证明代理不支持流式传输。")
    try:
        response_stream = model.generate_content(prompt, stream=True)
        full_response_text = ""
        for chunk in response_stream:
            if chunk.text:
                print(f"收到数据块: {chunk.text.strip()}")
                full_response_text += chunk.text
        
        print("流式请求成功！")
        print(f"完整响应: {full_response_text.strip()}")

    except Exception as e:
        print("流式请求失败！")
        print(f"捕获到异常: {type(e).__name__} - {e}")
        traceback.print_exc()

    finally:
        print("\n--- 诊断结束 ---")


if __name__ == "__main__":
    run_tests()