# Ralph-Planning

> 自动迭代循环 + 结构化规划：Claude Code 的高效自主开发工作流

## 概述

Ralph-Planning 是一个 Claude Code 插件，融合了两个强大的 AI 开发方法论：

- **[Ralph Wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)**: 通过 Stop Hook 实现的自动迭代循环
- **[Planning with Files](https://github.com/OthmanAdi/planning-with-files)**: 基于 Markdown 的结构化状态管理

### 核心价值

| 特性 | 说明 |
|------|------|
| 🔄 **自动迭代** | 无需人工驱动，自动循环执行任务 |
| 📋 **结构化规划** | 三文件模式管理任务、进度、日志 |
| 👁️ **可观测性** | 实时查看进度、当前任务、错误统计 |
| 🛠️ **可干预性** | 随时暂停、编辑计划、继续执行 |
| 🔁 **可恢复性** | 断点续传，支持长时间任务 |
| 📝 **可审计性** | 完整的决策记录和工作日志 |

## 安装

插件已安装在 `~/.claude/plugins/ralph-planning/`。

确保脚本有执行权限：

```bash
chmod +x ~/.claude/plugins/ralph-planning/scripts/*.sh
chmod +x ~/.claude/plugins/ralph-planning/hooks/*.sh
```

## 推荐启动方式

为了让循环流畅运行而不被权限确认打断，**强烈建议**使用以下方式启动 Claude Code：

```bash
claude --dangerously-skip-permissions
```

**安全建议**：
```bash
# 1. 在 Git 仓库中运行，方便回滚
git add -A && git commit -m "before ralph-plan"

# 2. 设置合理的 max-iterations 作为安全阀
/ralph-plan "任务" --max-iterations 30

# 3. 可选：在 Docker/虚拟机中运行以完全隔离
```

## 快速开始

### 1. 启动 Claude Code

```bash
# 进入项目目录
cd /path/to/your/project

# 使用跳过权限模式启动（推荐）
claude --dangerously-skip-permissions
```

### 2. 启动循环

```bash
/ralph-plan "构建一个 TODO REST API，包含 CRUD 操作和测试" --max-iterations 30
```

### 3. 完善任务计划

初始化后，编辑 `.claude/task_plan.md`：

```markdown
# 项目：TODO REST API

## 目标
构建功能完整的 TODO API

## 完成标准
- [ ] 所有 CRUD 端点可用
- [ ] 测试覆盖率 > 80%
- [ ] API 文档完整

## Phase 1: 初始化 ⏳
- [ ] 创建项目结构
- [ ] 配置依赖

## Phase 2: 实现 ⏳
- [ ] GET /todos
- [ ] POST /todos
...
```

### 4. 自动执行

Claude 会自动进入迭代循环：
1. 读取 task_plan.md 确认当前任务
2. 执行任务
3. 更新状态文件
4. 检查完成条件
5. 继续下一迭代

### 5. 监控进度

```bash
/ralph-status
```

### 6. 完成循环

当所有完成标准满足时，输出：
```
<promise>ALL_PHASES_COMPLETE</promise>
```

## 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `/ralph-plan` | 启动循环 | `/ralph-plan "任务" --max-iterations 30` |
| `/ralph-status` | 查看状态 | `/ralph-status` |
| `/ralph-pause` | 暂停循环 | `/ralph-pause "需要确认设计"` |
| `/ralph-continue` | 继续循环 | `/ralph-continue` |
| `/ralph-cancel` | 取消循环 | `/ralph-cancel` |

## 文件结构

```
.claude/
├── ralph-state.yaml    # 循环状态（系统管理）
├── task_plan.md        # 任务规划与进度（人机共读写）
└── notes.md            # 工作日志（AI 写入）
```

### ralph-state.yaml

```yaml
active: true
current_iteration: 7
max_iterations: 50
error_count: 2
consecutive_errors: 0
human_intervention_requested: false
```

### task_plan.md

```markdown
# 项目：[名称]

## 目标
[一句话描述]

## 完成标准
- [x] 标准1 ✓
- [ ] 标准2

## Phase 1: ... ✅
- [x] 任务1
- [x] 任务2

## Phase 2: ... 🔄
- [x] 任务3
- [ ] 任务4  ← **当前任务**

## 关键决策
| 决策 | 理由 | 迭代 |

## 遇到的问题
| 问题 | 解决方案 | 迭代 |

## 人工备注区
<!-- 人工添加的指导信息 -->
```

### notes.md

```markdown
# 工作日志

## 迭代 7 | 2024-01-08 10:52
**阶段**: Phase 2
**任务**: 实现 DELETE 端点

### 执行步骤
1. 读取 task_plan.md
2. 实现删除功能
3. 添加测试

### 发现
- 需要处理 404 情况

### 下一步
- 实现输入验证
```

## 工作流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    /ralph-plan "任务"                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  初始化                                                      │
│  - 创建 ralph-state.yaml                                    │
│  - 创建 task_plan.md 模板                                   │
│  - 创建 notes.md                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  迭代 N                                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Read task_plan.md  (刷新目标，确认任务)             │  │
│  │ 2. Read notes.md      (了解上下文)                     │  │
│  │ 3. 执行当前任务                                        │  │
│  │ 4. 更新 task_plan.md  (标记 [x])                       │  │
│  │ 5. 更新 notes.md      (添加日志)                       │  │
│  │ 6. Claude 尝试结束                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stop Hook 检查                                              │
│  - 人工介入请求?     → 暂停                                  │
│  - 连续错误超限?     → 暂停                                  │
│  - 达到最大迭代?     → 结束                                  │
│  - 检测到 <promise>? → 结束                                  │
│  - 否则             → 继续迭代 N+1                           │
└─────────────────────────────────────────────────────────────┘
```

## 人工介入

### 编辑任务计划

随时可以编辑 `.claude/task_plan.md`：
- 调整任务优先级
- 添加/删除任务
- 在"人工备注区"添加指导

### 暂停与继续

```bash
# 暂停
/ralph-pause "需要确认 API 设计"

# 编辑 task_plan.md
vim .claude/task_plan.md

# 继续
/ralph-continue
```

### 错误自动暂停

连续 3 次错误后自动暂停，等待人工检查。

## 最佳实践

### 1. 明确完成标准

```markdown
## 完成标准
- [ ] 所有 API 端点返回正确状态码
- [ ] 单元测试覆盖率 > 80%
- [ ] 无 linter 警告
```

### 2. 任务粒度适中

每个任务应能在一次迭代内完成：

```markdown
# ❌ 太大
- [ ] 实现整个 API

# ✅ 合适
- [ ] 实现 GET /todos 端点
- [ ] 实现 POST /todos 端点
```

### 3. 使用阶段检查点

```markdown
## Phase 1: 初始化 ✅
## Phase 2: 核心功能 🔄  ← 当前阶段
## Phase 3: 测试 ⏳
## Phase 4: 文档 ⏳
```

### 4. 记录决策和问题

```markdown
## 关键决策
| 决策 | 理由 | 迭代 |
|------|------|------|
| 使用 SQLite | 开发简单 | 2 |

## 遇到的问题
| 问题 | 解决方案 | 迭代 |
|------|----------|------|
| 导入错误 | 添加 __init__.py | 5 |
```

### 5. 设置合理的最大迭代

```bash
# 简单任务
/ralph-plan "..." --max-iterations 20

# 复杂项目
/ralph-plan "..." --max-iterations 100
```

## 适用场景

### ✅ 适合

- 有明确完成标准的开发任务
- 需要多步骤迭代的项目
- 可自动验证的工作（测试、linter）
- 绿地项目，可以放着过夜运行

### ❌ 不适合

- 需要频繁人工判断的任务
- 一次性简单操作
- 成功标准模糊的探索性工作

## 与原版的对比

| 特性 | Ralph 原版 | Planning 原版 | Ralph-Planning |
|------|-----------|--------------|----------------|
| 自动循环 | ✅ | ❌ | ✅ |
| 结构化规划 | ❌ | ✅ | ✅ |
| 进度可视化 | ❌ | ✅ | ✅ |
| 智能完成检测 | 🔶 | ❌ | ✅ |
| 错误追踪 | ❌ | ✅ | ✅ + 自动暂停 |
| 人工介入 | 🔶 | ✅ | ✅ + 暂停/继续 |

## 故障排除

### 循环不启动

检查状态文件：
```bash
cat .claude/ralph-state.yaml
```

确保 `active: true`。

### Hook 不生效

检查权限：
```bash
chmod +x ~/.claude/plugins/ralph-planning/hooks/stop-hook.sh
```

### 循环卡住

使用取消命令：
```bash
/ralph-cancel
```

## 参考资料

- [Ralph Wiggum 技术](https://ghuntley.com/ralph/)
- [Planning with Files](https://github.com/OthmanAdi/planning-with-files)
- [Claude Code 插件文档](https://docs.anthropic.com/claude-code/plugins)

## 许可证

MIT License
