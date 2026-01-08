---
description: "启动 Ralph-Planning 自动迭代循环"
argument_hint: '"任务描述" [--max-iterations N] [--completion-promise TEXT]'
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-plan.sh:*)", "Read", "Write", "Edit"]
---

# /ralph-plan 命令

启动一个结合自动循环和结构化规划的开发工作流。

## 用法

```
/ralph-plan "任务描述" [--max-iterations N] [--completion-promise TEXT]
```

## 参数

- `任务描述`: 要完成的任务（必需）
- `--max-iterations N`: 最大迭代次数，默认 50
- `--completion-promise TEXT`: 完成标志文本，默认 "ALL_PHASES_COMPLETE"

## 示例

```
/ralph-plan "构建一个 TODO REST API，包含 CRUD 操作和测试" --max-iterations 30
```

## 初始化后

执行初始化脚本后，你需要：

1. **完善任务计划**: 编辑 `.claude/task_plan.md`
   - 填写项目名称和目标
   - 定义完成标准
   - 细化各阶段的具体任务

2. **开始执行**: 系统会自动进入迭代循环

## 工作流程

每次迭代必须：
1. 读取 `task_plan.md` 确认当前任务
2. 读取 `notes.md` 了解上下文
3. 执行一个具体任务
4. 更新状态文件
5. 检查完成条件

## 完成循环

当所有完成标准都满足时，输出:
```
<promise>ALL_PHASES_COMPLETE</promise>
```

## 相关命令

- `/ralph-status` - 查看当前状态
- `/ralph-pause` - 暂停循环
- `/ralph-continue` - 继续循环
- `/ralph-cancel` - 取消循环
