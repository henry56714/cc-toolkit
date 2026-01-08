#!/bin/bash
# setup-ralph-plan.sh
# 初始化 Ralph-Planning 循环

set -e

PLUGIN_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
STATE_DIR=".claude"
STATE_FILE="$STATE_DIR/ralph-state.yaml"
TASK_PLAN="$STATE_DIR/task_plan.md"
NOTES="$STATE_DIR/notes.md"

# 默认值
MAX_ITERATIONS=50
COMPLETION_PROMISE="ALL_PHASES_COMPLETE"
PROMPT=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --completion-promise)
            COMPLETION_PROMISE="$2"
            shift 2
            ;;
        *)
            if [[ -z "$PROMPT" ]]; then
                PROMPT="$1"
            else
                PROMPT="$PROMPT $1"
            fi
            shift
            ;;
    esac
done

# 检查 prompt
if [[ -z "$PROMPT" ]]; then
    echo "❌ 错误: 请提供任务描述"
    echo "用法: /ralph-plan \"任务描述\" [--max-iterations N] [--completion-promise TEXT]"
    exit 1
fi

# 检查是否已有活跃循环
if [[ -f "$STATE_FILE" ]]; then
    ACTIVE=$(grep "^active:" "$STATE_FILE" | awk '{print $2}')
    if [[ "$ACTIVE" == "true" ]]; then
        echo "⚠️  已有活跃的 Ralph-Planning 循环"
        echo "使用 /ralph-cancel 取消当前循环，或 /ralph-status 查看状态"
        exit 1
    fi
fi

# 创建状态目录
mkdir -p "$STATE_DIR"

# 获取当前时间
STARTED_AT=$(date -Iseconds)

# 创建状态文件
cat > "$STATE_FILE" << EOF
# Ralph-Planning 循环状态
# 此文件由系统管理，请勿手动编辑

active: true
started_at: "$STARTED_AT"
current_iteration: 1
max_iterations: $MAX_ITERATIONS
completion_promise: "$COMPLETION_PROMISE"

# 原始任务描述
prompt: |
  $PROMPT

# 阶段检查点
checkpoints: {}

# 错误统计
error_count: 0
consecutive_errors: 0
max_consecutive_errors: 3

# 人工介入
human_intervention_requested: false
pause_reason: null
EOF

# 创建任务计划模板
cat > "$TASK_PLAN" << 'EOF'
# 项目：[项目名称]

## 目标
[一句话描述最终目标]

## 完成标准
- [ ] [标准1]
- [ ] [标准2]
- [ ] [标准3]

---

## Phase 1: 规划与准备 ⏳
- [ ] 分析需求
- [ ] 设计方案
- [ ] 准备环境

## Phase 2: 核心实现 ⏳
- [ ] [任务1]
- [ ] [任务2]

## Phase 3: 测试与完善 ⏳
- [ ] 编写测试
- [ ] 修复问题

## Phase 4: 文档与交付 ⏳
- [ ] 编写文档
- [ ] 最终检查

---

## 关键决策
| 决策 | 理由 | 迭代 |
|------|------|------|

## 遇到的问题
| 问题 | 解决方案 | 迭代 |
|------|----------|------|

---

## 人工备注区
<!-- 在这里添加任何需要 AI 注意的信息 -->

EOF

# 创建工作日志
cat > "$NOTES" << EOF
# 工作日志

<!-- 最新的迭代记录在最前面 -->

---
## 迭代 1 | $(date '+%Y-%m-%d %H:%M')
**状态**: 初始化

### 任务描述
$PROMPT

### 下一步
1. 读取并完善 task_plan.md
2. 根据任务描述填充具体阶段和任务
3. 开始执行第一个任务

EOF

echo "✅ Ralph-Planning 循环已初始化"
echo ""
echo "📁 状态文件: $STATE_FILE"
echo "📋 任务计划: $TASK_PLAN"
echo "📝 工作日志: $NOTES"
echo ""
echo "🔄 最大迭代次数: $MAX_ITERATIONS"
echo "🎯 完成标志: <promise>$COMPLETION_PROMISE</promise>"
echo ""
echo "💡 提示:"
echo "   - 使用 /ralph-status 查看当前状态"
echo "   - 使用 /ralph-pause 暂停循环"
echo "   - 使用 /ralph-cancel 取消循环"
echo ""
echo "🚀 开始执行任务..."
