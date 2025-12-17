#!/bin/bash

# 简洁版本
for stage in Stage1_Analyze.py Stage2_Analyze.py Stage3_Analyze.py Stage4_Analyze.py; do
    echo "执行: $stage"
    python3 "$stage" || exit 1
done

echo "所有阶段执行完成！"