---
description: "取消 Ralph-Planning 循环"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/ralph-cancel.sh)"]
---

# /ralph-cancel 命令

完全取消当前的 Ralph-Planning 循环。

## 用法

```
/ralph-cancel
```

## 说明

此命令会：
1. 将循环标记为非活跃
2. 保留所有状态文件供后续查看

## 保留的文件

- `.claude/ralph-state.yaml` - 循环状态记录
- `.claude/task_plan.md` - 任务计划
- `.claude/notes.md` - 工作日志

这些文件不会被删除，你可以：
- 查看已完成的工作
- 分析执行过程
- 手动继续未完成的任务
