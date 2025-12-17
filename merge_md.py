import os
from datetime import datetime

def merge_markdown_files():
    """合并outputs文件夹下的四个Markdown文件"""
    
    # 定义要合并的文件路径
    file_paths = [
        "outputs/stage1_output.md",
        "outputs/stage2_output.md", 
        "outputs/stage3_output.md",
        "outputs/stage4_output.md"
    ]
    
    # 输出文件名
    output_file = "经营分析报告.md"
    
    # 检查文件是否存在
    missing_files = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("错误：以下文件不存在：")
        for missing in missing_files:
            print(f"  - {missing}")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # 写入报告头部
            outfile.write(f"# 经营分析报告\n\n")
            outfile.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 逐个读取并合并文件
            for i, file_path in enumerate(file_paths, 1):
                # 添加部分标题
                outfile.write(f"## 第{i}部分\n\n")
                
                # 读取并写入文件内容
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                
                # 添加文件之间的分隔符
                if i < len(file_paths):
                    outfile.write("\n\n---\n\n")
        
        print(f"✅ 报告生成成功：{output_file}")
        print(f"📄 合并了 {len(file_paths)} 个文件")
        return True
        
    except Exception as e:
        print(f"❌ 合并文件时出错：{e}")
        return False

if __name__ == "__main__":
    merge_markdown_files()