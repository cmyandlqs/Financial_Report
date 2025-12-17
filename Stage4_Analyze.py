import os
import sys
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 加载环境变量
load_dotenv()

# ---------------- 配置区域 ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 输入文件路径
PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "stage4_prompt.md")
DATA_PATH = os.path.join(BASE_DIR, "data", "stage4.json")
# 关键：Stage 4 需要读取 Stage 3 的输出结果作为上下文
STAGE3_OUTPUT_PATH = os.path.join(BASE_DIR, "outputs", "stage3_output.md")

# 输出文件路径
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUTS_DIR, "stage4_output.md")
# ----------------------------------------

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
    print("🚀 正在初始化 Stage 4 (关键行动) 分析 Agent...")

    # 1. 准备输入数据
    # A. 读取 Prompt 模版
    prompt_text = load_file_content(PROMPT_PATH)
    
    # B. 读取 Stage 4 原始清单数据 (JSON)
    try:
        json_data_obj = json.loads(load_file_content(DATA_PATH))
        json_data_str = json.dumps(json_data_obj, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ 读取 Stage 4 JSON 数据失败: {e}")
        return

    # C. 读取 Stage 3 分析报告 (Markdown) -> 作为上下文Context
    # 如果 Stage 3 还没运行，这里会报错，提醒用户先运行 Stage 3
    try:
        stage3_context_str = load_file_content(STAGE3_OUTPUT_PATH)
        print(f"✅ 已加载 Stage 3 分析结果 ({len(stage3_context_str)} 字符)")
    except FileNotFoundError:
        print("❌ 错误: 未找到 Stage 3 的输出文件。")
        print(f"请先运行 'stage3_analyze.py' 生成: {STAGE3_OUTPUT_PATH}")
        return

    # 确保输出目录存在
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # 2. 初始化 LLM
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise EnvironmentError("请配置 DEEPSEEK_API_KEY")

    llm = init_chat_model(
        "deepseek-chat",
        model_provider="openai",
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com",
        temperature=0.2, # Stage 4 需要一定的推理能力，但不能太发散，0.2 比较稳妥
    )

    # 3. 构建 Chain
    # Prompt 中包含两个变量: {stage3_gap_analysis} 和 {input_json}
    prompt_template = ChatPromptTemplate.from_template(prompt_text)
    output_parser = StrOutputParser()
    chain = prompt_template | llm | output_parser

    # 4. 执行 Chain
    print("🤖 Agent 正在制定关键行动清单...")
    try:
        result = invoke_with_retry(chain, {
            "input_json": json_data_str,
            "stage3_gap_analysis": stage3_context_str
        })

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)

        print("-" * 30)
        print(f"🎉 Stage 4 关键行动报告生成成功！")
        print(f"📂 保存路径: {OUTPUT_FILE}")
        print("-" * 30)
        print("预览内容 (前500字符):\n")
        print(result[:500] + "...")

    except Exception as e:
        print(f"❌ 运行出错: {e}")
        if "Missing some input keys" in str(e):
            print("💡 提示：请检查 prompts/stage4.md 中是否将非变量的 { } 转义为 {{ }}")
        sys.exit(1)

if __name__ == "__main__":
    run_agent()