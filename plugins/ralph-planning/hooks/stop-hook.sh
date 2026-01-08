#!/bin/bash
# stop-hook.sh
# Ralph-Planning Stop Hook - 拦截退出并决定是否继续循环

set -e

STATE_DIR=".claude"
STATE_FILE="$STATE_DIR/ralph-state.yaml"
TASK_PLAN="$STATE_DIR/task_plan.md"
NOTES="$STATE_DIR/notes.md"

# 从 stdin 读取 hook 输入
HOOK_INPUT=$(cat)

# 辅助函数：解析 YAML 值
parse_yaml_value() {
    local key="$1"
    grep "^${key}:" "$STATE_FILE" 2>/dev/null | sed "s/^${key}: *//" | sed 's/^"\(.*\)"$/\1/'
}

# 辅助函数：更新 YAML 值
update_yaml_value() {
    local key="$1"
    local value="$2"
    local temp_file="${STATE_FILE}.tmp.$$"
    sed "s/^${key}: .*/${key}: ${value}/" "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"
}

# 辅助函数：清理并退出
cleanup_and_exit() {
    if [[ -f "$STATE_FILE" ]]; then
        update_yaml_value "active" "false"
    fi
    exit 0
}

# 辅助函数：获取最后的 assistant 消息
get_last_assistant_message() {
    local transcript_path
    transcript_path=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // empty')

    if [[ -z "$transcript_path" ]] || [[ ! -f "$transcript_path" ]]; then
        echo ""
        return
    fi

    local last_line
    last_line=$(grep '"role":"assistant"' "$transcript_path" 2>/dev/null | tail -1 || echo "")

    if [[ -z "$last_line" ]]; then
        echo ""
        return
    fi

    echo "$last_line" | jq -r '
        .message.content |
        if type == "array" then
            map(select(.type == "text")) |
            map(.text) |
            join("\n")
        else
            .
        end
    ' 2>/dev/null || echo ""
}

# 1. 检查状态文件是否存在
if [[ ! -f "$STATE_FILE" ]]; then
    exit 0  # 无活跃循环，允许退出
fi

# 2. 检查循环是否活跃
ACTIVE=$(parse_yaml_value "active")
if [[ "$ACTIVE" != "true" ]]; then
    exit 0  # 循环未激活，允许退出
fi

# 3. 解析状态
ITERATION=$(parse_yaml_value "current_iteration")
MAX_ITERATIONS=$(parse_yaml_value "max_iterations")
COMPLETION_PROMISE=$(parse_yaml_value "completion_promise")
CONSECUTIVE_ERRORS=$(parse_yaml_value "consecutive_errors")
MAX_CONSECUTIVE_ERRORS=$(parse_yaml_value "max_consecutive_errors")
HUMAN_INTERVENTION=$(parse_yaml_value "human_intervention_requested")

# 验证数值
ITERATION=${ITERATION:-1}
MAX_ITERATIONS=${MAX_ITERATIONS:-50}
CONSECUTIVE_ERRORS=${CONSECUTIVE_ERRORS:-0}
MAX_CONSECUTIVE_ERRORS=${MAX_CONSECUTIVE_ERRORS:-3}

# 4. 检查人工介入请求
if [[ "$HUMAN_INTERVENTION" == "true" ]]; then
    echo "⏸️  人工介入已请求，循环暂停" >&2
    cleanup_and_exit
fi

# 5. 检查连续错误阈值
if [[ $CONSECUTIVE_ERRORS -ge $MAX_CONSECUTIVE_ERRORS ]]; then
    echo "⚠️  连续错误次数过多 ($CONSECUTIVE_ERRORS)，暂停等待人工检查" >&2
    update_yaml_value "human_intervention_requested" "true"
    update_yaml_value "pause_reason" "\"consecutive_errors_exceeded\""
    cleanup_and_exit
fi

# 6. 检查最大迭代次数
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
    echo "🛑 已达到最大迭代次数 ($MAX_ITERATIONS)" >&2
    cleanup_and_exit
fi

# 7. 获取最后的 assistant 消息
LAST_OUTPUT=$(get_last_assistant_message)

# 8. 检测完成标志
if [[ -n "$LAST_OUTPUT" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
    # 使用 Perl 提取 <promise> 标签内容
    PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s; s/^\s+|\s+$//g; s/\s+/ /g' 2>/dev/null || echo "")

    if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" == "$COMPLETION_PROMISE" ]]; then
        echo "✅ 检测到完成标志: <promise>$COMPLETION_PROMISE</promise>" >&2
        cleanup_and_exit
    fi
fi

# 9. 智能完成检测：检查 task_plan.md 的完成标准
if [[ -f "$TASK_PLAN" ]]; then
    # 提取完成标准部分
    COMPLETION_SECTION=$(sed -n '/^## 完成标准/,/^---/p' "$TASK_PLAN" 2>/dev/null | head -n -1)

    if [[ -n "$COMPLETION_SECTION" ]]; then
        TOTAL_CRITERIA=$(echo "$COMPLETION_SECTION" | grep -c '\- \[' || echo "0")
        COMPLETED_CRITERIA=$(echo "$COMPLETION_SECTION" | grep -c '\- \[x\]' || echo "0")

        if [[ $TOTAL_CRITERIA -gt 0 ]] && [[ $TOTAL_CRITERIA -eq $COMPLETED_CRITERIA ]]; then
            # 所有完成标准都已满足，但还需要检查 promise
            if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" == "$COMPLETION_PROMISE" ]]; then
                echo "✅ 所有完成标准已满足!" >&2
                cleanup_and_exit
            fi
        fi
    fi
fi

# 10. 继续循环 - 更新迭代计数
NEXT_ITERATION=$((ITERATION + 1))
update_yaml_value "current_iteration" "$NEXT_ITERATION"

# 11. 重置连续错误计数（如果这次迭代成功完成）
update_yaml_value "consecutive_errors" "0"

# 12. 获取当前任务信息
CURRENT_TASK=""
if [[ -f "$TASK_PLAN" ]]; then
    # 尝试找到标记为当前任务的项
    CURRENT_TASK=$(grep -m1 '← \*\*当前任务\*\*' "$TASK_PLAN" 2>/dev/null | sed 's/← \*\*当前任务\*\*//' | sed 's/^- \[ \] //' || echo "")

    # 如果没有标记，找第一个未完成的任务
    if [[ -z "$CURRENT_TASK" ]]; then
        CURRENT_TASK=$(grep -m1 '^\- \[ \]' "$TASK_PLAN" 2>/dev/null | sed 's/^- \[ \] //' || echo "继续执行")
    fi
fi

# 13. 构建系统消息
SYSTEM_MSG="🔄 迭代 $NEXT_ITERATION/$MAX_ITERATIONS"
if [[ -n "$CURRENT_TASK" ]]; then
    SYSTEM_MSG="$SYSTEM_MSG | 任务: $CURRENT_TASK"
fi

# 14. 构建下一次迭代的 prompt
NEXT_PROMPT=$(cat << 'PROMPT_EOF'
继续执行任务。

**重要 - 每次迭代必须执行以下步骤:**

1. **恢复上下文**:
   - 读取 .claude/task_plan.md 确认当前阶段和任务
   - 读取 .claude/notes.md 查看最近的迭代记录

2. **执行当前任务**:
   - 找到第一个未完成的 [ ] 任务
   - 专注完成这一个任务

3. **更新状态文件**:
   - 在 task_plan.md 中将完成的任务标记为 [x]
   - 在 notes.md 顶部添加本次迭代记录

4. **检查完成条件**:
   - 如果"完成标准"中所有 [ ] 都变成 [x]
   - 并且你确认工作真正完成
   - 输出: <promise>ALL_PHASES_COMPLETE</promise>

如需人工介入，在 task_plan.md 的"人工备注区"说明原因。
PROMPT_EOF
)

# 15. 返回 JSON 阻止退出
jq -n \
    --arg prompt "$NEXT_PROMPT" \
    --arg msg "$SYSTEM_MSG" \
    '{
        "decision": "block",
        "reason": $prompt,
        "systemMessage": $msg
    }'
