#!/usr/bin/env python3
"""
从Markdown文件中提取标记的生词及其上下文句子。
生词用 **word** 格式标记。
"""

import re
import json
import sys
from pathlib import Path


def get_sentence_context(text: str, word: str, match_start: int, match_end: int) -> str:
    """获取生词所在的完整句子作为上下文"""
    # 向前找句子开头（标点或段落边界）
    sentence_start = match_start
    for i in range(match_start - 1, max(0, match_start - 500), -1):
        # 遇到句子结束标点后的空白，说明找到了上一句的结尾
        if text[i] in '.!?':
            # 跳过标点后的空白字符
            sentence_start = i + 1
            while sentence_start < match_start and text[sentence_start] in ' \t\n':
                sentence_start += 1
            break
        # 遇到连续两个换行符（段落边界）也视为句子开头
        if i > 0 and text[i] == '\n' and text[i-1] == '\n':
            sentence_start = i + 1
            while sentence_start < match_start and text[sentence_start] in ' \t\n':
                sentence_start += 1
            break
        if i == max(0, match_start - 500):
            sentence_start = i

    # 向后找句子结尾（标点或段落边界）
    sentence_end = match_end
    for i in range(match_end, min(len(text), match_end + 500)):
        # 遇到句子结束标点
        if text[i] in '.!?':
            sentence_end = i + 1
            break
        # 遇到连续两个换行符（段落边界）
        if i < len(text) - 1 and text[i] == '\n' and text[i+1] == '\n':
            sentence_end = i
            break
        if i == min(len(text), match_end + 500) - 1:
            sentence_end = i + 1

    # 提取句子并清理
    sentence = text[sentence_start:sentence_end].strip()
    # 移除所有 **word** 标记，只保留单词本身
    sentence = re.sub(r'\*\*([^*]+)\*\*', r'\1', sentence)
    # 清理多余空白（将换行符替换为空格，多个空格合并为一个）
    sentence = re.sub(r'\s+', ' ', sentence)
    return sentence.strip()


def extract_words_from_file(file_path: str) -> dict:
    """从文件中提取所有标记的生词及其上下文"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding='utf-8')

    # 使用文件名（不含扩展名）作为牌组名
    deck_name = path.stem

    # 匹配 **word** 格式
    pattern = r'\*\*([^*]+)\*\*'

    words_data = []
    seen_words = set()  # 避免重复

    for match in re.finditer(pattern, content):
        word = match.group(1).strip().lower()

        # 跳过已处理的词和非单词内容
        if word in seen_words:
            continue
        if not word or len(word) < 2:
            continue
        # 跳过纯数字或特殊字符
        if not re.match(r'^[a-zA-Z\'-]+$', word):
            continue

        seen_words.add(word)

        # 获取原始形式（保留大小写）
        original_word = match.group(1).strip()

        # 获取上下文句子
        sentence = get_sentence_context(content, word, match.start(), match.end())

        words_data.append({
            'word': original_word,
            'word_lower': word,
            'sentence': sentence,
            'translation': '',  # 待翻译
            'sentence_translation': '',  # 待翻译
        })

    return {
        'deck_name': deck_name,
        'file_path': str(path.absolute()),
        'word_count': len(words_data),
        'words': words_data
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_words.py <input_file> [output_file]")
        print("Example: python extract_words.py /path/to/article.md")
        print("")
        print("If output_file is not specified, prints JSON to stdout.")
        print("Deck name is derived from the input filename.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = extract_words_from_file(input_file)
        output = json.dumps(result, ensure_ascii=False, indent=2)

        if output_file:
            Path(output_file).write_text(output, encoding='utf-8')
            print(f"Extracted {result['word_count']} words to {output_file}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
