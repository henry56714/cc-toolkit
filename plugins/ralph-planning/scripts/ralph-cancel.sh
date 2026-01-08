#!/bin/bash
# ralph-cancel.sh
# 取消 Ralph-Planning 循环

STATE_FILE=".claude/ralph-state.yaml"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ 没有活跃的 Ralph-Planning 循环"
    exit 0
fi

# 标记为非活跃
sed -i "s/^active: .*/active: false/" "$STATE_FILE"

echo "🛑 Ralph-Planning 循环已取消"
echo ""
echo "状态文件已保留，你可以查看:"
echo "  - .claude/ralph-state.yaml (循环状态)"
echo "  - .claude/task_plan.md (任务计划)"
echo "  - .claude/notes.md (工作日志)"
