#!/bin/bash
# ralph-pause.sh
# 暂停 Ralph-Planning 循环

STATE_FILE=".claude/ralph-state.yaml"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ 没有活跃的 Ralph-Planning 循环"
    exit 1
fi

REASON="${1:-manual_pause}"

# 更新状态
sed -i "s/^human_intervention_requested: .*/human_intervention_requested: true/" "$STATE_FILE"
sed -i "s/^pause_reason: .*/pause_reason: \"$REASON\"/" "$STATE_FILE"

echo "⏸️  Ralph-Planning 循环已暂停"
echo "原因: $REASON"
echo ""
echo "使用 /ralph-continue 继续循环"
