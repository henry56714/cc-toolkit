# CC Toolkit

Claude Code 插件集合。

## 插件列表

### ralph-planning

自动迭代循环 + 结构化规划工具，结合自动循环机制和三文件状态管理。

**命令**：
- `/ralph-plan` - 开始规划任务
- `/ralph-status` - 查看任务状态
- `/ralph-continue` - 继续执行
- `/ralph-pause` - 暂停任务
- `/ralph-cancel` - 取消任务

### markdown-anki

从 Markdown 文件提取 `**word**` 标记的生词，翻译并生成 Anki 牌组。

**特性**：
- 智能去重 + 翻译缓存
- 分批翻译，避免上下文限制
- 支持单文件和批量目录处理

## 安装

```bash
# 添加市场
/plugin marketplace add henry56714/cc-toolkit

# 安装插件
/plugin install ralph-planning@cc-toolkit
/plugin install markdown-anki@cc-toolkit
```

## 本地开发

```bash
# 直接加载插件目录
claude --plugin-dir ./plugins/ralph-planning
claude --plugin-dir ./plugins/markdown-anki
```

## License

MIT
