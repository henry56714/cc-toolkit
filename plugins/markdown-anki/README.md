# Markdown-Anki 生词卡片生成器

从 Markdown 文件提取标记的生词，使用 Claude Code 翻译并生成 Anki 单词卡片。支持翻译缓存和分批处理（每批30个单词），避免重复翻译和超过上下文限制。

## 快速开始

### 基本使用流程

1. 在 Markdown 文件中用 `**word**` 标记生词
2. 运行提取脚本（自动去重并查询缓存）
3. 自动分批生成待翻译文件（每批最多30个单词）
4. 使用 Claude Code 翻译每批单词
5. 保存翻译到缓存
6. 所有批次完成后自动生成 Anki 导入文件
7. 导入到 Anki

### 单文件处理示例

```bash
# Step 1: 提取生词并查询缓存
python3 scripts/process_file.py /path/to/article.md
# 输出：生成批次文件（如果单词 > 30 会分成多批）

# Step 2: 使用 Claude Code 翻译第一批单词
# 在 Claude Code 中输入："请帮我翻译这个文件中的单词"
# 将翻译结果保存为 translation_batch_1.json

# Step 3: 保存翻译
python3 scripts/process_file.py /tmp/article_to_translate_batch_1.json translation_batch_1.json

# Step 4: 如果有多批，重复步骤2-3
# 所有批次完成后，脚本会自动合并生成 article.txt
```

### 批量处理示例

```bash
# Step 1: 批量提取生词并查询缓存（如《老友记》S01 所有剧集）
python3 scripts/process_directory.py /path/to/S01/
# 输出：自动分批生成待翻译文件

# Step 2: 使用 Claude Code 翻译每批单词
# 按照提示逐批翻译

# Step 3: 保存每批翻译
python3 scripts/process_directory.py /path/to/S01/ translation_batch_1.json

# Step 4: 重复步骤2-3直到所有批次完成
# 所有批次完成后，自动合并生成 S01.txt 文件
```

## 核心特性：翻译缓存

### 自动去重机制

✅ **文件内去重**：同一文件中的重复单词只提取一次
✅ **全局去重**：查询缓存，已翻译的单词不再重复翻译
✅ **持久化存储**：所有翻译自动保存到 `translation_cache.json`
✅ **效率提升**：处理《老友记》24 集，后期翻译量减少 70%+

### 缓存文件位置

```
~/.claude/skills/markdown-anki/translation_cache.json
```

### 缓存管理命令

```bash
# 查看缓存统计
python3 scripts/translation_cache.py stats

# 查询单个单词
python3 scripts/translation_cache.py get hump

# 手动添加单词
python3 scripts/translation_cache.py add hump "n. 驼背；隆起" "So does he have a hump?" "那他有驼背吗？"
```

### 导入已有翻译

如果您有之前生成的 Anki 文件，可以导入到缓存中：

```bash
# 单个文件
python3 scripts/import_to_cache.py /path/to/old_anki_file.txt

# 批量导入
python3 scripts/import_to_cache.py /path/to/anki/*.txt
```

## Anki 配置指南

生成的文件使用 Basic 卡片类型会导致显示不完整。需要创建自定义卡片类型。

### 第一步：创建笔记类型

1. 打开 Anki
2. **工具 (Tools)** → **管理笔记类型 (Manage Note Types)**
3. 点击 **添加 (Add)** → 选择 **Basic**
4. 输入名称：**Vocabulary**（或您喜欢的名称）

### 第二步：配置字段

在笔记类型列表中选择刚创建的类型，点击 **字段 (Fields)**：

1. 删除默认的 "Front" 和 "Back" 字段
2. 添加以下 5 个字段：
   - `Word`
   - `Translation`
   - `Sentence`
   - `SentenceTranslation`
   - `Tags`

### 第三步：配置卡片模板

点击 **卡片 (Cards)** 按钮，配置以下内容：

#### 前端模板（Front Template）

```html
<div class="card">
  <div class="word">{{Word}}</div>
  <div class="sentence">{{Sentence}}</div>
</div>
```

#### 后端模板（Back Template）

```html
<div class="card">
  <div class="word">{{Word}}</div>
  <div class="translation">{{Translation}}</div>

  <hr class="separator">

  <div class="sentence">{{Sentence}}</div>
  <div class="sentence-translation">{{SentenceTranslation}}</div>
</div>
```

#### 样式（Styling）

```css
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #333;
  background-color: #fff;
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

/* 单词样式 */
.word {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 15px;
}

/* 翻译样式 */
.translation {
  font-size: 22px;
  color: #e74c3c;
  margin-bottom: 25px;
  font-weight: 500;
}

/* 分隔线 */
.separator {
  border: none;
  border-top: 2px solid #ecf0f1;
  margin: 25px 0;
}

/* 例句样式 */
.sentence {
  font-size: 18px;
  color: #34495e;
  line-height: 1.6;
  margin-bottom: 12px;
  text-align: left;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

/* 例句翻译样式 */
.sentence-translation {
  font-size: 16px;
  color: #7f8c8d;
  line-height: 1.6;
  text-align: left;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #95a5a6;
}

/* 移动端适配 */
@media (max-width: 600px) {
  .card {
    font-size: 18px;
    padding: 15px;
  }

  .word {
    font-size: 28px;
  }

  .translation {
    font-size: 20px;
  }

  .sentence {
    font-size: 16px;
  }

  .sentence-translation {
    font-size: 14px;
  }
}
```

### 第四步：导入数据

1. **文件 (File)** → **导入 (Import)**
2. 选择生成的 `.txt` 文件
3. 设置：
   - **类型 (Type)**：选择刚创建的 **Vocabulary**
   - **字段分隔符 (Fields separated by)**：**Tab**
   - **字段映射**：确认顺序为 Word → Translation → Sentence → SentenceTranslation → Tags

### 卡片效果预览

**正面**（复习时）：
```
━━━━━━━━━━━━━━━━━━━━
      hump

  So does he have a hump?
━━━━━━━━━━━━━━━━━━━━
```

**反面**（点击显示答案）：
```
━━━━━━━━━━━━━━━━━━━━
      hump
   n. 驼背；隆起

─────────────────────

  So does he have a hump?
  那他有驼背吗？
━━━━━━━━━━━━━━━━━━━━
```

## 高级功能

### TTS 语音朗读

使用 AwesomeTTS 插件可以为 `Word` 和 `Sentence` 字段添加英语发音。

### 自定义样式

修改样式中的以下部分可调整外观：
- **字体大小**：`.word`、`.translation` 等的 `font-size`
- **颜色**：各个 `color` 属性
- **间距**：`margin` 和 `padding` 值

### 批量操作技巧

处理大量文件时：

```bash
# 批量提取所有文件
python3 scripts/batch_extract.py /path/to/directory/

# 查看需要翻译的单词总数
python3 scripts/translation_cache.py stats

# 生成合并文件
python3 scripts/generate_anki.py /tmp/directory/*.json output.txt
```

## 工作流程详解

### 完整处理流程

```
Markdown 文件 (标记 **word**)
    ↓
提取脚本 (文件内去重)
    ↓
查询翻译缓存 (全局去重)
    ↓
分离：已缓存 ＋ 未缓存
    ↓
分批生成待翻译文件 (每批最多30个单词)
    ↓
使用 Claude Code 翻译每批单词
    ↓
保存翻译到缓存
    ↓
检查所有批次是否完成
    ↓
自动合并生成 Anki TSV 文件
    ↓
导入到 Anki
```

### 去重层级

1. **提取阶段**：同一文件内的重复单词只提取一次
2. **查询缓存**：已翻译的单词直接使用缓存，不再翻译
3. **保存缓存**：新翻译的单词自动去重后保存

### 缓存数据结构

```json
{
  "hump": {
    "translation": "n. 驼背；隆起",
    "sentence_examples": [
      {
        "sentence": "So does he have a hump?",
        "sentence_translation": "那他有驼背吗？"
      }
    ]
  }
}
```

## 故障排查

### 导入 Anki 后显示不正确

原因：使用了 Basic 卡片类型
解决：按照"Anki 配置指南"创建自定义笔记类型

### 缓存未生效

检查：
1. 缓存文件是否存在：`~/.claude/skills/markdown-anki/translation_cache.json`
2. 是否使用了集成工作流脚本
3. 单词是否使用小写查询

### 文件编码问题

确保所有文件使用 UTF-8 编码。

## 翻译规则

1. **分批处理**：每批最多 30 个单词，避免超过 Claude Code 上下文限制
2. **格式要求**：翻译包含词性（n./v./adj. 等）
3. **语境准确**：根据例句选择合适词义
4. **自然流畅**：翻译口语化，符合中文习惯

## 使用 Claude Code 翻译

脚本会自动分批生成待翻译文件，请按以下步骤使用 Claude Code 翻译：

1. 脚本输出批次文件路径（例如：`/tmp/article_to_translate_batch_1.json`）
2. 在 Claude Code 中输入："请帮我翻译这个文件中的单词，按照文件中提供的格式返回翻译结果"
3. Claude Code 会返回 JSON 格式的翻译结果
4. 将翻译结果保存为文件（例如：`translation_batch_1.json`）
5. 运行保存命令将翻译保存到缓存并生成 Anki 文件

**翻译格式示例：**

```json
[
  {
    "word": "hump",
    "translation": "n. 驼背；隆起",
    "sentence": "So does he have a hump?",
    "sentence_translation": "那他有驼背吗？"
  }
]
```

## 注意事项

1. **备份缓存**：定期备份 `translation_cache.json`
2. **单词大小写**：缓存使用小写存储，显示保留原始大小写
3. **例句去重**：同一单词的相同例句不会重复存储
4. **文件路径**：使用绝对路径避免路径错误

## 目录结构

```
~/.claude/skills/markdown-anki/
├── README.md                     # 本文档
├── SKILL.md                      # Skill 定义
├── translation_cache.json        # 翻译缓存（自动生成）
└── scripts/
    ├── extract_words.py          # 提取生词
    ├── batch_extract.py          # 批量提取
    ├── generate_anki.py          # 生成 Anki 文件
    ├── translation_cache.py      # 缓存管理器
    ├── import_to_cache.py        # 导入已有翻译
    ├── process_file.py           # 单文件集成工作流
    └── process_directory.py      # 批量集成工作流
```

## 性能优化效果

使用翻译缓存处理《老友记》24 集示例：

| 集数 | 新单词数 | 翻译量减少 |
|-----|---------|----------|
| 第 1 集 | 100+ | 0% |
| 第 2-5 集 | 50-70 | 30-50% |
| 第 10+ 集 | 20-30 | 70%+ |
| 第 20+ 集 | 10-15 | 85%+ |

随着缓存积累，翻译效率显著提升。
