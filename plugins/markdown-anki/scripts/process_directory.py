#!/usr/bin/env python3
"""
批量目录处理集成脚本

自动处理整个目录的 Markdown 文件，包括：
1. 批量提取所有文件的生词（文件内去重）
2. 查询缓存（全局去重）
3. 分批输出需要翻译的单词（每批最多30个）
4. 使用 Claude Code 翻译每批单词
5. 保存翻译到缓存
6. 生成合并的 Anki 文件

确保所有单词只翻译一次，避免上下文过长。
"""

import json
import sys
from pathlib import Path

from batch_extract import extract_words_from_directory
from translation_cache import TranslationCache
from generate_anki import generate_anki_tsv
from config import get_output_dir

# 每批翻译的最大单词数
BATCH_SIZE = 30


def process_directory(directory: str, output_file: str = None) -> dict:
    """
    处理整个目录的 Markdown 文件

    Args:
        directory: 包含 Markdown 文件的目录
        output_file: 输出的 Anki 文件名

    Returns:
        处理结果统计
    """
    # 1. 批量提取生词
    print(f"[1/5] 批量提取生词：{directory}")
    all_data = extract_words_from_directory(directory, '/tmp')

    if not all_data:
        print("  没有找到标记的生词，退出")
        return {'total': 0, 'cached': 0, 'new': 0}

    total_words = sum(data['word_count'] for data in all_data)
    print(f"  ✓ 从 {len(all_data)} 个文件中提取到 {total_words} 个生词（已去重）")

    # 2. 查询缓存并全局去重
    print("\n[2/5] 查询翻译缓存并全局去重")
    cache = TranslationCache()

    # 跟踪所有单词（全局去重）
    global_seen_words = set()
    all_cached_words = []
    all_uncached_words = []

    for file_data in all_data:
        for word_item in file_data['words']:
            word = word_item['word_lower']

            # 全局去重：如果这个单词在之前的文件中已经出现过，跳过
            if word in global_seen_words:
                continue

            global_seen_words.add(word)
            cached_translation = cache.get(word)

            if cached_translation:
                # 使用缓存的翻译
                word_item['translation'] = cached_translation['translation']
                examples = cached_translation.get('sentence_examples', [])
                if examples:
                    word_item['sentence_translation'] = examples[0]['sentence_translation']
                else:
                    word_item['sentence_translation'] = ''
                all_cached_words.append(word_item)
            else:
                # 添加 deck_name 信息
                word_item['deck_name'] = file_data['deck_name']
                all_uncached_words.append(word_item)

    print(f"  ✓ 全局去重后：{len(global_seen_words)} 个唯一单词")
    print(f"  ✓ 找到 {len(all_cached_words)} 个已缓存的单词")
    print(f"  ✓ 需要翻译 {len(all_uncached_words)} 个新单词")

    # 3. 输出需要翻译的单词（分批处理）
    if all_uncached_words:
        print("\n[3/5] 需要翻译的单词列表：")
        print("─" * 60)

        dir_name = Path(directory).name

        # 计算需要分成多少批
        total_batches = (len(all_uncached_words) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n  总共 {len(all_uncached_words)} 个新单词，将分成 {total_batches} 批处理（每批最多 {BATCH_SIZE} 个）")

        # 分批保存待翻译单词到临时文件
        temp_files = []
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min((batch_num + 1) * BATCH_SIZE, len(all_uncached_words))
            batch_words = all_uncached_words[start_idx:end_idx]

            # 生成批次文件名
            if total_batches == 1:
                temp_file = Path('/tmp') / f"{dir_name}_to_translate.json"
            else:
                temp_file = Path('/tmp') / f"{dir_name}_to_translate_batch_{batch_num + 1}.json"

            batch_data = {
                'directory': directory,
                'batch_info': f"批次 {batch_num + 1}/{total_batches}",
                'words': batch_words
            }
            temp_file.write_text(
                json.dumps(batch_data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            temp_files.append(str(temp_file))

            print(f"\n批次 {batch_num + 1}/{total_batches}：{len(batch_words)} 个单词 -> {temp_file}")

        print("\n" + "─" * 60)
        print("\n📝 使用 Claude Code 翻译单词：")
        print("\n对于每个批次文件，请执行以下步骤：")
        print("\n1. 在 Claude Code 中输入：")
        print("   \"请帮我翻译这个文件中的单词，按照文件中提供的格式返回翻译结果\"")
        print("\n2. 将翻译结果保存为 JSON 文件（例如：translation_batch_1.json）")
        print("\n3. 运行以下命令保存翻译：")
        for i, temp_file in enumerate(temp_files, 1):
            print(f"   python3 scripts/process_directory.py {directory} translation_batch_{i}.json")

        print("\n" + "─" * 60)
        print("\n翻译格式示例（需列出单词的所有常用词义，与词典一致）：")
        print('[')
        print('  {')
        print('    "word": "example",')
        print('    "translation": "n. 例子；范例；榜样 v. 作为...的例子",')
        print('    "sentence": "This is an example.",')
        print('    "sentence_translation": "这是一个例子。"')
        print('  }')
        print(']')

        print("\n💡 提示：")
        print(f"  - 每批最多 {BATCH_SIZE} 个单词，确保不超过 Claude Code 的上下文限制")
        print("  - 翻译完一批后再处理下一批")
        print("  - 所有批次处理完成后，会自动合并生成最终的 Anki 文件")

        return {
            'total': total_words,
            'unique': len(global_seen_words),
            'cached': len(all_cached_words),
            'new': len(all_uncached_words),
            'temp_files': temp_files,
            'total_batches': total_batches
        }

    else:
        print("\n[3/5] 所有单词都已缓存，无需翻译")

        # 4. 重建完整数据（包含缓存的翻译）
        print("\n[4/5] 重建完整数据")

        # 为每个文件重新填充翻译
        for file_data in all_data:
            for word_item in file_data['words']:
                word = word_item['word_lower']
                cached_translation = cache.get(word)
                if cached_translation:
                    word_item['translation'] = cached_translation['translation']
                    examples = cached_translation.get('sentence_examples', [])
                    if examples:
                        word_item['sentence_translation'] = examples[0]['sentence_translation']

        # 5. 生成 Anki 文件
        print("\n[5/5] 生成 Anki 文件")

        if output_file is None:
            dir_name = Path(directory).name
            output_dir = get_output_dir()
            output_file = str(output_dir / f"{dir_name}.txt")

        generate_anki_tsv(all_data, output_file, deck_name=dir_name)
        print(f"  ✓ 已生成：{output_file}")

        print("\n完成！")
        print(f"  总单词数：{total_words}")
        print(f"  唯一单词：{len(global_seen_words)}")
        print(f"  使用缓存：{len(all_cached_words)}")
        print(f"  新翻译：0")

        return {
            'total': total_words,
            'unique': len(global_seen_words),
            'cached': len(all_cached_words),
            'new': 0,
            'output_file': output_file
        }


def save_and_generate(temp_file: str, translation_file: str, output_file: str = None):
    """
    保存翻译并生成 Anki 文件（支持单批和多批处理）

    Args:
        temp_file: 待翻译单词的临时文件
        translation_file: 翻译后的 JSON 文件
        output_file: 输出文件名
    """
    # 加载待翻译数据
    uncached_data = json.loads(Path(temp_file).read_text(encoding='utf-8'))
    directory = uncached_data['directory']

    # 加载翻译数据
    translations = json.loads(Path(translation_file).read_text(encoding='utf-8'))

    # 确保是列表
    if isinstance(translations, dict):
        translations = [translations]

    print(f"\n[4/5] 保存翻译到缓存")
    cache = TranslationCache()

    # 创建翻译字典（小写单词 -> 翻译）并保存到缓存
    translated_count = 0
    for trans in translations:
        word_lower = trans['word'].lower()

        # 保存到缓存
        cache.add(
            word=trans['word'],
            translation=trans['translation'],
            sentence=trans.get('sentence', ''),
            sentence_translation=trans['sentence_translation']
        )
        translated_count += 1

    print(f"  ✓ 已保存 {translated_count} 个翻译到缓存")

    # 检查是否是批次处理
    batch_info = uncached_data.get('batch_info', '')
    if batch_info:
        print(f"\n  当前批次：{batch_info}")

        # 检查是否所有批次都已完成
        dir_name = Path(directory).name
        check_and_merge_batches(directory, dir_name, output_file)
    else:
        # 单批处理，直接生成 Anki 文件
        print("\n[5/5] 重新提取并生成 Anki 文件")
        all_data = extract_words_from_directory(directory, '/tmp')

        # 填充所有翻译
        for file_data in all_data:
            for word_item in file_data['words']:
                word = word_item['word_lower']
                cached_translation = cache.get(word)
                if cached_translation:
                    word_item['translation'] = cached_translation['translation']
                    examples = cached_translation.get('sentence_examples', [])
                    if examples:
                        word_item['sentence_translation'] = examples[0]['sentence_translation']

        # 生成 Anki 文件
        if output_file is None:
            dir_name = Path(directory).name
            output_dir = get_output_dir()
            output_file = str(output_dir / f"{dir_name}.txt")

        generate_anki_tsv(all_data, output_file, deck_name=dir_name)
        print(f"  ✓ 已生成：{output_file}")

        print("\n完成！")


def check_and_merge_batches(directory: str, dir_name: str, output_file: str = None):
    """
    检查所有批次是否都已翻译完成，如果是则合并生成最终 Anki 文件

    Args:
        directory: 源目录
        dir_name: 目录名称
        output_file: 输出文件名
    """
    # 查找所有相关的批次文件
    tmp_dir = Path('/tmp')
    batch_files = sorted(tmp_dir.glob(f"{dir_name}_to_translate_batch_*.json"))

    if not batch_files:
        print("  ⚠️  未找到其他批次文件，可能是单批处理")
        return

    total_batches = len(batch_files)
    print(f"\n  检测到 {total_batches} 个批次文件")

    # 读取所有批次文件，检查是否都已翻译
    all_uncached_words = []
    untranslated_batches = []
    cache = TranslationCache()

    for batch_file in batch_files:
        batch_data = json.loads(batch_file.read_text(encoding='utf-8'))
        batch_num = batch_data.get('batch_info', '').split('/')[0].split()[-1]

        # 检查这批单词是否都已翻译（是否在缓存中）
        all_translated = True

        for word_item in batch_data['words']:
            word = word_item['word_lower']
            cached_translation = cache.get(word)

            if not cached_translation:
                all_translated = False
                untranslated_batches.append(batch_num)
                break

        if not all_translated:
            # 这批还有未翻译的单词
            pass
        else:
            # 这批已全部翻译
            all_uncached_words.extend(batch_data['words'])

    # 如果还有未翻译的批次，提示用户继续
    if untranslated_batches:
        print(f"\n  ⚠️  还有 {len(untranslated_batches)} 个批次未完成翻译：批次 {', '.join(untranslated_batches)}")
        print("\n  请继续翻译剩余批次，然后运行对应的保存命令")
        return

    # 所有批次都已完成，生成最终 Anki 文件
    print(f"\n  ✓ 所有 {total_batches} 个批次都已完成翻译")
    print("\n[5/5] 重新提取并生成最终 Anki 文件")

    all_data = extract_words_from_directory(directory, '/tmp')

    # 填充所有翻译
    for file_data in all_data:
        for word_item in file_data['words']:
            word = word_item['word_lower']
            cached_translation = cache.get(word)
            if cached_translation:
                word_item['translation'] = cached_translation['translation']
                examples = cached_translation.get('sentence_examples', [])
                if examples:
                    word_item['sentence_translation'] = examples[0]['sentence_translation']

    # 生成 Anki 文件
    if output_file is None:
        output_dir = get_output_dir()
        output_file = str(output_dir / f"{dir_name}.txt")

    generate_anki_tsv(all_data, output_file, deck_name=dir_name)
    print(f"  ✓ 已生成：{output_file}")

    print("\n完成！所有批次已合并并生成 Anki 文件")

    # 提示清理临时文件
    print(f"\n💡 提示：临时批次文件位于 /tmp/{dir_name}_to_translate_batch_*.json")
    print("  可以手动删除这些临时文件")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  # 第一步：批量提取生词并查询缓存")
        print("  python3 process_directory.py <directory>")
        print()
        print("  # 第二步：使用 Claude Code 翻译每批单词并保存")
        print("  python3 process_directory.py <directory> <translation.json> [output.txt]")
        print()
        print("说明：")
        print("  - 当单词数量 ≤ 30 时，生成一个文件，翻译后直接生成 Anki 文件")
        print("  - 当单词数量 > 30 时，分批生成多个文件，每批翻译完成后自动检查")
        print("  - 所有批次完成后，自动合并生成最终 Anki 文件")
        sys.exit(1)

    directory = sys.argv[1]

    if not Path(directory).is_dir():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if len(sys.argv) == 2:
        # 第一步：提取并查询缓存
        process_directory(directory)

    elif len(sys.argv) >= 3:
        # 第二步：保存翻译并生成
        translation_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None

        if not Path(translation_file).exists():
            print(f"Error: Translation file not found: {translation_file}")
            sys.exit(1)

        # 查找临时文件（支持批次和非批次）
        dir_name = Path(directory).name
        temp_file = None

        # 先尝试查找批次文件（从第二个参数的文件名推断批次号）
        if 'batch' in translation_file.lower():
            import re
            batch_match = re.search(r'batch[_\s]*(\d+)', translation_file.lower())
            if batch_match:
                batch_num = batch_match.group(1)
                temp_file = Path('/tmp') / f"{dir_name}_to_translate_batch_{batch_num}.json"

        # 如果不是批次文件或未找到，尝试非批次文件
        if temp_file is None or not temp_file.exists():
            temp_file = Path('/tmp') / f"{dir_name}_to_translate.json"

        if not temp_file.exists():
            print(f"Error: Temp file not found: {temp_file}")
            print("请先运行第一步：python3 process_directory.py <directory>")
            sys.exit(1)

        save_and_generate(str(temp_file), translation_file, output_file)


if __name__ == '__main__':
    main()
