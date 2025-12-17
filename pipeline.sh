#!/bin/bash

for stage in Stage1_Analyze.py Stage2_Analyze.py Stage3_Analyze.py Stage4_Analyze.py; do
    echo "执行: $stage"
    python3 "$stage" || exit 1
done

echo "开始合并Markdown文件..."
if [ -f "merge_md.py" ]; then
    python3 merge_md.py
    echo "✅ 经营分析报告合并完成！"
else
    echo "警告：merge_md.py 文件不存在，跳过合并"
fi

echo "所有阶段执行完成！"