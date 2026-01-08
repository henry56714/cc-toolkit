#!/usr/bin/env python3
"""
批量提取目录中所有Markdown文件的生词。

用法：
    python batch_extract.py <input_dir> [output_dir]

输出：
    - 每个输入文件生成对应的JSON文件
    - output_dir默认为 /tmp/<input_dir_name>/
    - 每个文件的deck_name使用文件名（不含扩展名）
"""

import sys
from pathlib import Path

# 导入同目录的extract_words模块
sys.path.insert(0, str(Path(__file__).parent))
from extract_words import extract_words_from_file


def batch_extract(input_dir: str, output_dir: str | None = None, pattern: str = "*.md") -> list[str]:
    """
    批量提取目录中所有markdown文件的生词。

    Args:
        input_dir: 输入目录，包含标记了生词的markdown文件
        output_dir: 输出目录，存放生成的JSON文件。默认为 /tmp/<input_dir_name>/
        pattern: 文件匹配模式，默认 *.md

    Returns:
        生成的JSON文件路径列表
    """
    import json

    input_path = Path(input_dir)

    # 默认输出目录：/tmp/<目录名>/
    if output_dir is None:
        output_dir = f"/tmp/{input_path.name}"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    md_files = sorted(input_path.glob(pattern))
    if not md_files:
        print(f"No files matching '{pattern}' in {input_dir}")
        return []

    output_files = []
    total_words = 0

    for md_file in md_files:
        try:
            result = extract_words_from_file(str(md_file))

            if result['word_count'] == 0:
                print(f"  {md_file.name}: no words marked, skipping")
                continue

            # 输出文件名使用原文件名
            output_file = output_path / f"{md_file.stem}.json"
            output_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )

            output_files.append(str(output_file))
            total_words += result['word_count']
            print(f"  {md_file.name}: {result['word_count']} words -> {output_file.name}")

        except Exception as e:
            print(f"  {md_file.name}: Error - {e}")

    print(f"\nTotal: {len(output_files)} files, {total_words} words")
    print(f"Output directory: {output_path}")
    return output_files


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_extract.py <input_dir> [output_dir]")
        print("")
        print("Examples:")
        print("  python batch_extract.py /path/to/articles/")
        print("  python batch_extract.py /path/to/S01/ /tmp/S01_words/")
        print("")
        print("If output_dir is not specified, uses /tmp/<input_dir_name>/")
        print("")
        print("Output naming:")
        print("  - Each file's deck_name = filename (without extension)")
        print("  - Anki output filename = directory name (when using generate_anki.py)")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Extracting words from: {input_dir}")
    batch_extract(input_dir, output_dir)


if __name__ == '__main__':
    main()
