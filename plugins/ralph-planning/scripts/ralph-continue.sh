#!/bin/bash
# ralph-continue.sh
# 继续 Ralph-Planning 循环

STATE_FILE=".claude/ralph-state.yaml"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ 没有 Ralph-Planning 循环可以继续"
    exit 1
fi

# 检查是否已暂停
INTERVENTION=$(grep "^human_intervention_requested:" "$STATE_FILE" | awk '{print $2}')

if [[ "$INTERVENTION" != "true" ]]; then
    echo "ℹ️  循环未处于暂停状态"
    exit 0
fi

# 重置暂停状态
sed -i "s/^human_intervention_requested: .*/human_intervention_requested: false/" "$STATE_FILE"
sed -i "s/^pause_reason: .*/pause_reason: null/" "$STATE_FILE"
sed -i "s/^consecutive_errors: .*/consecutive_errors: 0/" "$STATE_FILE"
sed -i "s/^active: .*/active: true/" "$STATE_FILE"

echo "▶️  Ralph-Planning 循环已继续"
echo ""
echo "循环将在下次迭代时恢复执行"
