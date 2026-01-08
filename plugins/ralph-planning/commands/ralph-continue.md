---
description: "继续暂停的 Ralph-Planning 循环"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/ralph-continue.sh)"]
---

# /ralph-continue 命令

恢复之前暂停的 Ralph-Planning 循环。

## 用法

```
/ralph-continue
```

## 说明

此命令会：
1. 重置人工介入标志
2. 清除连续错误计数
3. 重新激活循环

循环将在下次 Claude 尝试结束会话时继续执行。

## 前置条件

- 存在已暂停的循环
- 已解决导致暂停的问题
