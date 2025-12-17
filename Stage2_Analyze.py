import os
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "stage2_prompt.md")
DATA_PATH = os.path.join(BASE_DIR, "data", "stage1&2.json")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
OUTPUT_FILE = os.path.join(OUTPUTS_DIR, "stage2_output.md")


def load_prompt(prompt_path: str) -> str:
    """读取 Stage2 提示词模板，并将数据占位符转换为链路变量。"""
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    return prompt_text.replace("{{INPUT_JSON_HERE}}", "{input_json}")


def load_stage2_data(json_path: str) -> str:
    """读取 Stage2 数据文件并序列化为字符串，便于传递给 Prompt。"""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"未找到数据文件: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f), ensure_ascii=False, indent=2)


def run_agent():
    # 1. 读取 prompt 与数据
    prompt_text = load_prompt(PROMPT_PATH)
    json_data_str = load_stage2_data(DATA_PATH)

    # 确保输出目录存在
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # 2. 初始化 LLM（使用 init_chat_model 新格式）
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise EnvironmentError("缺少 DEEPSEEK_API_KEY 环境变量，请在 .env 或系统环境中配置。")

    llm = init_chat_model(
        "deepseek-chat",
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com",
        temperature=0.1,
        timeout=60,
    )

    # 3. 构建 Chain (LCEL 语法)
    prompt_template = ChatPromptTemplate.from_template(prompt_text)
    output_parser = StrOutputParser()
    chain = prompt_template | llm | output_parser

    # 4. 执行 Chain
    print("🤖 Agent 正在进行经营分析运算（Stage2）...")
    try:
        result = chain.invoke({"input_json": json_data_str})

        # 5. 保存结果
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)

        print("-" * 30)
        print(f"🎉 报告生成成功！已保存至: {OUTPUT_FILE}")
        print("-" * 30)
        print("预览内容:\n")
        print(result)

    except Exception as e:
        print(f"❌ 运行出错: {e}")


if __name__ == "__main__":
    run_agent()