---
description: "暂停 Ralph-Planning 循环"
argument_hint: "[原因]"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/ralph-pause.sh:*)"]
---

# /ralph-pause 命令

暂停当前的 Ralph-Planning 循环，等待人工介入。

## 用法

```
/ralph-pause [原因]
```

## 参数

- `原因`: 可选，暂停的原因说明

## 使用场景

- 需要人工审查当前进度
- 发现需要澄清的需求
- 想要调整任务计划
- 需要手动修复某些问题

## 示例

```
/ralph-pause "需要确认 API 设计方案"
```

## 恢复执行

使用 `/ralph-continue` 命令恢复循环。
