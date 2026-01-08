---
description: "显示 Ralph-Planning 帮助信息"
---

# Ralph-Planning 帮助

## 概述

Ralph-Planning 是一个结合自动迭代循环和结构化规划的 Claude Code 插件。它融合了：
- **Ralph Wiggum** 的自动循环机制
- **Planning with Files** 的三文件状态管理

## 核心概念

### 三文件模式

| 文件 | 用途 |
|------|------|
| `.claude/ralph-state.yaml` | 循环状态（系统管理） |
| `.claude/task_plan.md` | 任务规划与进度 |
| `.claude/notes.md` | 工作日志与笔记 |

### 自动循环

通过 Stop Hook 实现自动迭代：
1. Claude 执行任务后尝试退出
2. Hook 检查完成条件
3. 未完成则注入新 prompt 继续

## 命令列表

| 命令 | 说明 |
|------|------|
| `/ralph-plan` | 启动循环 |
| `/ralph-status` | 查看状态 |
| `/ralph-pause` | 暂停循环 |
| `/ralph-continue` | 继续循环 |
| `/ralph-cancel` | 取消循环 |

## 快速开始

```bash
# 1. 启动循环
/ralph-plan "构建一个 TODO API" --max-iterations 30

# 2. 完善 task_plan.md 中的任务

# 3. 循环自动执行，直到完成或达到最大迭代

# 4. 查看进度
/ralph-status
```

## 完成条件

循环在以下情况结束：
1. 输出 `<promise>ALL_PHASES_COMPLETE</promise>`
2. 达到最大迭代次数
3. 人工暂停/取消
4. 连续错误过多

## 最佳实践

1. **明确完成标准**: 在 task_plan.md 中定义可验证的标准
2. **任务粒度适中**: 每个任务应能在一次迭代内完成
3. **及时更新状态**: 完成任务后立即标记 [x]
4. **记录问题**: 遇到问题写入"遇到的问题"表

## 人工介入

可以随时编辑 `.claude/task_plan.md`:
- 调整任务优先级
- 添加/删除任务
- 在"人工备注区"添加指导

然后使用 `/ralph-continue` 继续。
