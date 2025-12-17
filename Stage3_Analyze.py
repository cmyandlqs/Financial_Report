import os
import sys
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # 建议使用标准库(或保持你原本的init_chat_model)
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 加载环境变量
load_dotenv()

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "stage3.md")
DATA_PATH = os.path.join(BASE_DIR, "data", "stage3.json")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUTS_DIR, "stage3_output.md")

def load_file_content(file_path: str) -> str:
    """通用文件读取函数"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def invoke_with_retry(chain, inputs: dict, max_retries: int = 3, delay: float = 2.0) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            print(f"⚠️ 第 {attempt} 次调用 LLM 失败: {e}")
            if attempt == max_retries:
                print("❌ 已达到最大重试次数，终止当前阶段。")
                raise
            time.sleep(delay)

def run_agent():
    # 1. 读取 Prompt 原始内容 (不做 Python replace，直接交给 LangChain)
    prompt_text = load_file_content(PROMPT_PATH)
    
    # 2. 读取 JSON 数据字符串
    json_data_obj = json.loads(load_file_content(DATA_PATH))
    # 转换为字符串，确保不含中文乱码
    json_data_str = json.dumps(json_data_obj, ensure_ascii=False, indent=2)

    # 确保输出目录存在
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # 3. 初始化 LLM
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise EnvironmentError("请配置 DEEPSEEK_API_KEY")

    llm = init_chat_model(
        "deepseek-chat",
        model_provider="openai", # DeepSeek 兼容 OpenAI 协议
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com",
        temperature=0.1,
    )

    # 4. 构建 Chain
    # 注意：这里直接使用 from_template，它会自动解析 prompt_text 中的 {input_json}
    prompt_template = ChatPromptTemplate.from_template(prompt_text)
    output_parser = StrOutputParser()
    chain = prompt_template | llm | output_parser

    # 5. 执行 Chain
    print("🤖 Agent 正在进行经营分析运算（Stage3）...")
    try:
        result = invoke_with_retry(chain, {"input_json": json_data_str})

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)

        print("-" * 30)
        print(f"🎉 报告生成成功！已保存至: {OUTPUT_FILE}")
        print("-" * 30)
        print("预览内容 (前500字符):\n")
        print(result[:500] + "...")

    except Exception as e:
        print(f"❌ 运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()