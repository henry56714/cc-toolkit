---
name: markdown-anki
description: "从 Markdown 提取 **word** 粗体标记的单词/生词，翻译单词和例句，生成 Anki 牌组。触发词：Anki、生词、单词卡、提取单词、背单词、牌组、翻译单词、粗体单词、markdown单词。"
---

# Markdown Anki 生词牌组生成器

从 Markdown 文件提取 `**word**` 标记的生词，自动查询缓存，仅翻译未缓存的单词，生成 Anki 可导入的牌组。

## 核心特性

✅ **智能去重**：文件内去重 + 全局缓存去重，确保每个单词只翻译一次
✅ **翻译缓存**：自动保存翻译到 `translation_cache.json`，持久化存储
✅ **分批翻译**：超过30个单词自动分批，避免超过 Claude Code 上下文限制
✅ **批量处理**：支持单文件和整个目录批量处理
✅ **效率提升**：随着缓存积累，翻译量可减少 70% 以上

## 快速使用

### 单文件处理

```bash
# 第一步：提取生词并查询缓存
python3 scripts/process_file.py /path/to/article.md
# 脚本会自动分批生成待翻译文件（每批最多30个单词）

# 第二步：使用 Claude Code 翻译每批单词
# 在 Claude Code 中输入："请帮我翻译这个文件中的单词"
# 将翻译结果保存为 translation_batch_1.json

# 第三步：保存翻译并生成 Anki 文件
python3 scripts/process_file.py /tmp/article_to_translate_batch_1.json translation_batch_1.json
# 重复步骤2-3直到所有批次完成，最终自动合并生成 Anki 文件
```

### 批量目录处理

```bash
# 第一步：批量提取生词并查询缓存
python3 scripts/process_directory.py /path/to/S01/
# 自动分批生成待翻译文件

# 第二步：使用 Claude Code 翻译每批单词
# 按照提示逐批翻译

# 第三步：保存翻译并生成合并文件
python3 scripts/process_directory.py /path/to/S01/ translation_batch_1.json
# 所有批次完成后自动合并生成最终 Anki 文件
```

## 工作流程

```
Markdown 文件 (**word** 标记)
    ↓
1. 提取生词 (文件内去重)
    ↓
2. 查询翻译缓存 (全局去重)
    ↓
3. 分批生成待翻译文件 (每批最多30个单词)
    ↓
4. 使用 Claude Code 翻译每批单词
    ↓
5. 保存翻译到缓存
    ↓
6. 检查所有批次是否完成
    ↓
7. 自动合并生成 Anki TSV 文件
    ↓
8. 导入到 Anki
```

## Anki 卡片字段

| 字段 | 内容 | TTS |
|------|------|-----|
| Word | 英文单词 | ✓ |
| Translation | 中文释义（含词性） | |
| Sentence | 英文例句 | ✓ |
| SentenceTranslation | 例句翻译 | |
| Tags | 牌组名（文件名） | |

## 翻译缓存管理

```bash
# 查看缓存统计
python3 scripts/translation_cache.py stats

# 查询单词
python3 scripts/translation_cache.py get hump

# 导入已有 Anki 文件到缓存
python3 scripts/import_to_cache.py /path/to/anki/*.txt
```

## 翻译规则

1. **分批处理**：每批最多 30 个单词，避免超过上下文限制
2. **格式要求**：translation 包含词性（n./v./adj. 等）
3. **完整词义**：列出单词的所有常用词义，与英语词典保持一致，不能只给出和例句相关的一个意思
4. **自然流畅**：翻译口语化，符合中文习惯

## 使用 Claude Code 翻译

脚本会自动分批生成待翻译文件，请在 Claude Code 中翻译每批单词：

**操作步骤：**

1. 脚本会输出批次文件路径（例如：`/tmp/article_to_translate_batch_1.json`）
2. 在 Claude Code 中输入："请帮我翻译这个文件中的单词，按照文件中提供的格式返回翻译结果"
3. Claude Code 会返回 JSON 格式的翻译结果
4. 将翻译结果保存为文件（例如：`translation_batch_1.json`）
5. 运行保存命令将翻译保存到缓存

**翻译格式示例：**

```json
[
  {
    "word": "hump",
    "translation": "n. 驼峰；隆起；驼背 v. 使隆起；弓起（背）；艰难行进",
    "sentence": "So does he have a hump?",
    "sentence_translation": "那他有驼背吗？"
  },
  {
    "word": "chalk",
    "translation": "n. 粉笔；白垩 v. 用粉笔写/画；记录",
    "sentence": "Wait, does he eat chalk?",
    "sentence_translation": "等等，他吃粉笔吗？"
  }
]
```

## 完整文档

详细的使用说明、Anki 配置指南、故障排查等，请查看：

**[README.md](README.md)**

## 配置文件

通过 `config.json` 可以设置 Anki 文件的固定输出目录：

```json
{
  "output_dir": "~/anki_output"
}
```

**配置说明：**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `output_dir` | Anki 文件输出目录 | 当前工作目录 |

- 支持 `~` 表示用户主目录
- 目录不存在时会自动创建
- 不配置则输出到当前工作目录（保持兼容）

## 目录结构

```
~/.claude/skills/markdown-anki/
├── README.md                     # 完整使用文档
├── SKILL.md                      # 本文件
├── config.json                   # 配置文件（输出目录等）
├── translation_cache.json        # 翻译缓存（自动生成）
└── scripts/
    ├── config.py                 # 配置管理模块
    ├── extract_words.py          # 提取生词
    ├── batch_extract.py          # 批量提取
    ├── generate_anki.py          # 生成 Anki 文件
    ├── translation_cache.py      # 缓存管理器
    ├── import_to_cache.py        # 导入已有翻译
    ├── process_file.py           # 单文件集成工作流 ⭐
    └── process_directory.py      # 批量集成工作流 ⭐
```

## 性能示例

处理《老友记》24 集的翻译效率：

- **第 1 集**：100+ 新单词
- **第 2-5 集**：50-70 新单词（减少 30-50%）
- **第 10+ 集**：20-30 新单词（减少 70%+）
- **第 20+ 集**：10-15 新单词（减少 85%+）
