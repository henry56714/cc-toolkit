#!/bin/bash
# ralph-status.sh
# 显示 Ralph-Planning 循环状态

STATE_FILE=".claude/ralph-state.yaml"
TASK_PLAN=".claude/task_plan.md"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ 没有活跃的 Ralph-Planning 循环"
    exit 0
fi

# 解析状态
parse_yaml() {
    grep "^${1}:" "$STATE_FILE" 2>/dev/null | sed "s/^${1}: *//" | sed 's/^"\(.*\)"$/\1/'
}

ACTIVE=$(parse_yaml "active")
ITERATION=$(parse_yaml "current_iteration")
MAX_ITER=$(parse_yaml "max_iterations")
STARTED=$(parse_yaml "started_at")
ERRORS=$(parse_yaml "error_count")
CONSECUTIVE=$(parse_yaml "consecutive_errors")
INTERVENTION=$(parse_yaml "human_intervention_requested")
PAUSE_REASON=$(parse_yaml "pause_reason")

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Ralph-Planning 循环状态                          ║"
echo "╠══════════════════════════════════════════════════════════════╣"

if [[ "$ACTIVE" == "true" ]]; then
    echo "║  状态: 🟢 运行中                                             ║"
else
    echo "║  状态: 🔴 已停止                                             ║"
fi

printf "║  迭代: %d / %d                                              ║\n" "$ITERATION" "$MAX_ITER"
echo "║  开始时间: $STARTED"
printf "║  错误统计: 总计 %d, 连续 %d                                  ║\n" "$ERRORS" "$CONSECUTIVE"

if [[ "$INTERVENTION" == "true" ]]; then
    echo "║  ⚠️  人工介入已请求: $PAUSE_REASON"
fi

echo "╠══════════════════════════════════════════════════════════════╣"

# 显示任务进度
if [[ -f "$TASK_PLAN" ]]; then
    echo "║  任务进度:                                                   ║"

    # 统计各阶段完成情况
    TOTAL_TASKS=$(grep -c '^\- \[' "$TASK_PLAN" 2>/dev/null) || TOTAL_TASKS=0
    COMPLETED_TASKS=$(grep -c '^\- \[x\]' "$TASK_PLAN" 2>/dev/null) || COMPLETED_TASKS=0

    # 确保是数字
    TOTAL_TASKS=${TOTAL_TASKS:-0}
    COMPLETED_TASKS=${COMPLETED_TASKS:-0}

    if [[ $TOTAL_TASKS -gt 0 ]]; then
        PROGRESS=$((COMPLETED_TASKS * 100 / TOTAL_TASKS))
        printf "║  [$COMPLETED_TASKS/$TOTAL_TASKS] %d%% 完成                                          ║\n" "$PROGRESS"

        # 进度条
        BAR_WIDTH=40
        FILLED=$((PROGRESS * BAR_WIDTH / 100))
        EMPTY=$((BAR_WIDTH - FILLED))
        printf "║  ["
        printf "%${FILLED}s" | tr ' ' '█'
        printf "%${EMPTY}s" | tr ' ' '░'
        printf "]  ║\n"
    fi

    # 显示当前任务
    CURRENT=$(grep -m1 '← \*\*当前任务\*\*' "$TASK_PLAN" 2>/dev/null | sed 's/← \*\*当前任务\*\*//' | sed 's/^- \[ \] //')
    if [[ -z "$CURRENT" ]]; then
        CURRENT=$(grep -m1 '^\- \[ \]' "$TASK_PLAN" 2>/dev/null | sed 's/^- \[ \] //')
    fi

    if [[ -n "$CURRENT" ]]; then
        echo "║                                                              ║"
        echo "║  📌 当前任务: $CURRENT"
    fi
fi

echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  命令:                                                        ║"
echo "║    /ralph-pause   - 暂停循环                                  ║"
echo "║    /ralph-continue - 继续循环                                 ║"
echo "║    /ralph-cancel  - 取消循环                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
