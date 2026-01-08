#!/usr/bin/env python3
"""
从翻译后的JSON数据生成Anki可导入的TSV文件。

字段设计（支持TTS朗读）：
- word: 英文单词（可启用TTS）
- translation: 中文释义
- sentence: 英文例句（可启用TTS）
- sentence_translation: 例句翻译
- tags: 标签（牌组名，来自文件名）
"""

import json
import sys
from pathlib import Path


def generate_anki_tsv(data: dict | list, output_path: str, deck_name: str = None) -> None:
    """
    生成Anki可导入的TSV文件。

    支持单个data dict或多个data的list（批量处理）。

    TSV格式：word<TAB>translation<TAB>sentence<TAB>sentence_translation<TAB>tags
    每个字段独立，便于Anki配置TTS和卡片模板。
    """
    lines = []

    # 统一处理：单个dict转为list
    data_list = data if isinstance(data, list) else [data]

    # 确定牌组名
    if deck_name is None:
        deck_name = data_list[0].get('deck_name', 'Default')

    # Anki导入指令（文件头部）
    header = [
        '#separator:tab',
        f'#deck:{deck_name}',
        '#columns:word\ttranslation\tsentence\tsentence_translation\ttags',
    ]

    for file_data in data_list:
        tags = file_data.get('deck_name', '')

        for item in file_data['words']:
            word = item['word']
            translation = item.get('translation', '')
            sentence = item.get('sentence', '')
            sentence_translation = item.get('sentence_translation', '')

            # 清理特殊字符
            sentence = sentence.replace('\t', ' ').replace('\n', ' ')
            sentence_translation = sentence_translation.replace('\t', ' ').replace('\n', ' ')
            translation = translation.replace('\t', ' ').replace('\n', ' ')

            # TSV行：5个独立字段
            line = f"{word}\t{translation}\t{sentence}\t{sentence_translation}\t{tags}"
            lines.append(line)

    output = '\n'.join(header + lines)
    Path(output_path).write_text(output, encoding='utf-8')
    print(f"Generated Anki file: {output_path} ({len(lines)} cards)")


def get_output_name(input_files: list[str]) -> str:
    """
    根据输入文件自动确定输出文件名。

    单文件：使用文件名（如 article.json -> article.txt）
    多文件：使用共同父目录名（如 S01/*.json -> S01.txt）
    """
    if len(input_files) == 1:
        return Path(input_files[0]).stem + '.txt'
    else:
        # 找共同父目录
        parent = Path(input_files[0]).parent
        return parent.name + '.txt'


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_anki.py <input_json> [output_file]")
        print("       python generate_anki.py <input1.json> <input2.json> ... [output_file]")
        print("")
        print("If output_file is not specified:")
        print("  - Single file: uses input filename (article.json -> article.txt)")
        print("  - Multiple files: uses parent directory name (S01/*.json -> S01.txt)")
        print("")
        print("TSV columns: word, translation, sentence, sentence_translation, tags")
        print("Tags are derived from each input file's deck_name (filename)")
        sys.exit(1)

    args = sys.argv[1:]

    # 判断最后一个参数是输出文件还是输入文件
    if args[-1].endswith('.txt') or args[-1].endswith('.tsv'):
        output_file = args[-1]
        input_files = args[:-1]
    else:
        input_files = args
        output_file = get_output_name(input_files)

    if not input_files:
        print("Error: No input files specified", file=sys.stderr)
        sys.exit(1)

    try:
        if len(input_files) == 1:
            # 单文件模式
            data = json.loads(Path(input_files[0]).read_text(encoding='utf-8'))
            generate_anki_tsv(data, output_file)
        else:
            # 多文件批量模式
            all_data = []
            for input_file in sorted(input_files):
                data = json.loads(Path(input_file).read_text(encoding='utf-8'))
                all_data.append(data)
            generate_anki_tsv(all_data, output_file)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
