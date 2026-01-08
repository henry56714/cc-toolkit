#!/usr/bin/env python3
"""
从已生成的 Anki TSV 文件导入单词到翻译缓存

这个工具可以将已有的 Anki 导出文件导入到缓存中，避免重复翻译。
"""

import sys
from pathlib import Path
from translation_cache import TranslationCache


def import_from_anki_file(anki_file: str, cache: TranslationCache) -> int:
    """
    从 Anki TSV 文件导入单词到缓存

    Args:
        anki_file: Anki TSV 文件路径
        cache: 翻译缓存实例

    Returns:
        导入的单词数量
    """
    path = Path(anki_file)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {anki_file}")

    content = path.read_text(encoding='utf-8')
    lines = content.strip().split('\n')

    imported = 0
    for line in lines:
        # 跳过注释行（以 # 开头）
        if line.startswith('#'):
            continue

        parts = line.split('\t')
        if len(parts) < 4:
            continue

        word = parts[0].strip()
        translation = parts[1].strip()
        sentence = parts[2].strip()
        sentence_translation = parts[3].strip()

        # 跳过空数据
        if not word or not translation:
            continue

        # 添加到缓存
        cache.add(word, translation, sentence, sentence_translation)
        imported += 1

    return imported


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_to_cache.py <anki_file.txt> [anki_file2.txt ...]")
        print("")
        print("Import words from Anki TSV files to translation cache.")
        print("")
        print("Example:")
        print("  python import_to_cache.py /path/to/0101.txt")
        print("  python import_to_cache.py /path/to/S01/*.txt")
        sys.exit(1)

    anki_files = sys.argv[1:]
    cache = TranslationCache()

    total_imported = 0
    for anki_file in anki_files:
        try:
            imported = import_from_anki_file(anki_file, cache)
            total_imported += imported
            print(f"Imported {imported} words from {anki_file}")
        except Exception as e:
            print(f"Error processing {anki_file}: {e}", file=sys.stderr)

    stats = cache.get_stats()
    print(f"\nTotal imported: {total_imported} words")
    print(f"Cache stats: {stats['total_words']} words, {stats['total_examples']} examples")


if __name__ == '__main__':
    main()
