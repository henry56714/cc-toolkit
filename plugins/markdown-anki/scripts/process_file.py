#!/usr/bin/env python3
"""
单文件处理集成脚本

自动处理单个 Markdown 文件，包括：
1. 提取生词（文件内去重）
2. 查询缓存（全局去重）
3. 分批输出需要翻译的单词（每批最多30个）
4. 使用 Claude Code 翻译每批单词
5. 保存翻译到缓存
6. 生成 Anki 文件

确保所有单词只翻译一次，避免上下文过长。
"""

import json
import sys
from pathlib import Path

# 导入其他模块
from extract_words import extract_words_from_file
from translation_cache import TranslationCache
from generate_anki import generate_anki_tsv
from config import get_output_dir

# 每批翻译的最大单词数
BATCH_SIZE = 30


def process_file(markdown_file: str, output_dir: str = None) -> dict:
    """
    处理单个 Markdown 文件

    Args:
        markdown_file: Markdown 文件路径
        output_dir: 输出目录，默认为当前目录

    Returns:
        处理结果统计
    """
    # 1. 提取生词（文件内已去重）
    print(f"[1/5] 提取生词：{markdown_file}")
    data = extract_words_from_file(markdown_file)
    total_words = data['word_count']
    print(f"  ✓ 提取到 {total_words} 个生词（已去重）")

    if total_words == 0:
        print("  没有找到标记的生词，退出")
        return {'total': 0, 'cached': 0, 'new': 0}

    # 2. 查询缓存（全局去重）
    print("\n[2/5] 查询翻译缓存")
    cache = TranslationCache()

    cached_words = []
    uncached_words = []

    for word_item in data['words']:
        word = word_item['word_lower']
        cached_translation = cache.get(word)

        if cached_translation:
            # 使用缓存的翻译
            word_item['translation'] = cached_translation['translation']
            # 对于例句翻译，优先使用缓存的第一个例句
            examples = cached_translation.get('sentence_examples', [])
            if examples:
                word_item['sentence_translation'] = examples[0]['sentence_translation']
            else:
                word_item['sentence_translation'] = ''
            cached_words.append(word_item)
        else:
            uncached_words.append(word_item)

    print(f"  ✓ 找到 {len(cached_words)} 个已缓存的单词")
    print(f"  ✓ 需要翻译 {len(uncached_words)} 个新单词")

    # 3. 输出需要翻译的单词（分批处理）
    if uncached_words:
        print("\n[3/5] 需要翻译的单词列表：")
        print("─" * 60)

        # 计算需要分成多少批
        total_batches = (len(uncached_words) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n  总共 {len(uncached_words)} 个新单词，将分成 {total_batches} 批处理（每批最多 {BATCH_SIZE} 个）")

        # 分批保存待翻译单词到临时文件
        temp_files = []
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min((batch_num + 1) * BATCH_SIZE, len(uncached_words))
            batch_words = uncached_words[start_idx:end_idx]

            # 生成批次文件名
            if total_batches == 1:
                temp_file = Path('/tmp') / f"{data['deck_name']}_to_translate.json"
            else:
                temp_file = Path('/tmp') / f"{data['deck_name']}_to_translate_batch_{batch_num + 1}.json"

            batch_data = {
                'deck_name': data['deck_name'],
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
            print(f"   python3 scripts/process_file.py {temp_file} translation_batch_{i}.json")

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
            'cached': len(cached_words),
            'new': len(uncached_words),
            'temp_files': temp_files,
            'total_batches': total_batches
        }

    else:
        print("\n[3/5] 所有单词都已缓存，无需翻译")

        # 4. 生成 Anki 文件
        print("\n[4/5] 生成 Anki 文件")
        data['words'] = cached_words

        if output_dir is None:
            output_dir = get_output_dir()
        else:
            output_dir = Path(output_dir)

        output_file = output_dir / f"{data['deck_name']}.txt"
        generate_anki_tsv(data, str(output_file))
        print(f"  ✓ 已生成：{output_file}")

        print("\n[5/5] 完成！")
        print(f"  总单词数：{total_words}")
        print(f"  使用缓存：{len(cached_words)}")
        print(f"  新翻译：0")

        return {
            'total': total_words,
            'cached': len(cached_words),
            'new': 0,
            'output_file': str(output_file)
        }


def save_and_generate(temp_file: str, translation_file: str, output_dir: str = None):
    """
    保存翻译并生成 Anki 文件（支持单批和多批处理）

    Args:
        temp_file: 待翻译单词的临时文件
        translation_file: 翻译后的 JSON 文件
        output_dir: 输出目录
    """
    # 加载待翻译数据
    uncached_data = json.loads(Path(temp_file).read_text(encoding='utf-8'))

    # 加载翻译数据
    translations = json.loads(Path(translation_file).read_text(encoding='utf-8'))

    # 确保是列表
    if isinstance(translations, dict):
        translations = [translations]

    print(f"\n[4/5] 保存翻译到缓存")
    cache = TranslationCache()

    # 更新未缓存单词的翻译
    translated_count = 0
    for word_item in uncached_data['words']:
        word = word_item['word_lower']

        # 在翻译数据中查找对应的翻译
        for trans in translations:
            if trans['word'].lower() == word:
                word_item['translation'] = trans['translation']
                word_item['sentence_translation'] = trans['sentence_translation']

                # 保存到缓存
                cache.add(
                    word=trans['word'],
                    translation=trans['translation'],
                    sentence=trans.get('sentence', word_item['sentence']),
                    sentence_translation=trans['sentence_translation']
                )
                translated_count += 1
                break

    print(f"  ✓ 已保存 {translated_count} 个翻译到缓存")

    # 检查是否是批次处理
    batch_info = uncached_data.get('batch_info', '')
    if batch_info:
        print(f"\n  当前批次：{batch_info}")

        # 检查是否所有批次都已完成
        deck_name = uncached_data['deck_name']
        check_and_merge_batches(deck_name, output_dir)
    else:
        # 单批处理，直接生成 Anki 文件
        print("\n[5/5] 生成 Anki 文件")

        if output_dir is None:
            output_dir = get_output_dir()
        else:
            output_dir = Path(output_dir)

        output_file = output_dir / f"{uncached_data['deck_name']}.txt"
        generate_anki_tsv(uncached_data, str(output_file))
        print(f"  ✓ 已生成：{output_file}")

        print("\n完成！")


def check_and_merge_batches(deck_name: str, output_dir: str = None):
    """
    检查所有批次是否都已翻译完成，如果是则合并生成最终 Anki 文件

    Args:
        deck_name: 牌组名称
        output_dir: 输出目录
    """
    # 查找所有相关的批次文件
    tmp_dir = Path('/tmp')
    batch_files = sorted(tmp_dir.glob(f"{deck_name}_to_translate_batch_*.json"))

    if not batch_files:
        print("  ⚠️  未找到其他批次文件，可能是单批处理")
        return

    total_batches = len(batch_files)
    print(f"\n  检测到 {total_batches} 个批次文件")

    # 读取所有批次文件，检查是否都已翻译
    all_words = []
    untranslated_batches = []

    for batch_file in batch_files:
        batch_data = json.loads(batch_file.read_text(encoding='utf-8'))
        batch_num = batch_data.get('batch_info', '').split('/')[0].split()[-1]

        # 检查这批单词是否都已翻译（是否在缓存中）
        cache = TranslationCache()
        all_translated = True

        for word_item in batch_data['words']:
            word = word_item['word_lower']
            cached_translation = cache.get(word)

            if cached_translation:
                # 使用缓存的翻译
                word_item['translation'] = cached_translation['translation']
                examples = cached_translation.get('sentence_examples', [])
                if examples:
                    word_item['sentence_translation'] = examples[0]['sentence_translation']
            else:
                all_translated = False
                untranslated_batches.append(batch_num)
                break

        if all_translated:
            all_words.extend(batch_data['words'])

    # 如果还有未翻译的批次，提示用户继续
    if untranslated_batches:
        print(f"\n  ⚠️  还有 {len(untranslated_batches)} 个批次未完成翻译：批次 {', '.join(untranslated_batches)}")
        print("\n  请继续翻译剩余批次，然后运行对应的保存命令")
        return

    # 所有批次都已完成，生成最终 Anki 文件
    print(f"\n  ✓ 所有 {total_batches} 个批次都已完成翻译")
    print("\n[5/5] 生成最终 Anki 文件")

    if output_dir is None:
        output_dir = get_output_dir()
    else:
        output_dir = Path(output_dir)

    final_data = {
        'deck_name': deck_name,
        'words': all_words
    }

    output_file = output_dir / f"{deck_name}.txt"
    generate_anki_tsv(final_data, str(output_file))
    print(f"  ✓ 已生成：{output_file}")

    print("\n完成！所有批次已合并并生成 Anki 文件")
    print(f"  总单词数：{len(all_words)}")

    # 询问是否删除临时批次文件
    print(f"\n💡 提示：临时批次文件位于 /tmp/{deck_name}_to_translate_batch_*.json")
    print("  可以手动删除这些临时文件")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  # 第一步：提取生词并查询缓存")
        print("  python3 process_file.py <markdown_file> [output_dir]")
        print()
        print("  # 第二步：使用 Claude Code 翻译每批单词并保存")
        print("  python3 process_file.py <batch_file> <translation.json> [output_dir]")
        print()
        print("说明：")
        print("  - 当单词数量 ≤ 30 时，生成一个文件，翻译后直接生成 Anki 文件")
        print("  - 当单词数量 > 30 时，分批生成多个文件，每批翻译完成后自动检查")
        print("  - 所有批次完成后，自动合并生成最终 Anki 文件")
        print("  - output_dir 为可选参数，指定 Anki 文件的输出目录（默认为当前目录）")
        sys.exit(1)

    if len(sys.argv) == 2 or (len(sys.argv) == 3 and not sys.argv[2].endswith('.json')):
        # 第一步：提取并查询缓存
        markdown_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None

        if not Path(markdown_file).exists():
            print(f"Error: File not found: {markdown_file}")
            sys.exit(1)

        process_file(markdown_file, output_dir)

    elif len(sys.argv) >= 3:
        # 第二步：保存翻译并生成
        temp_file = sys.argv[1]
        translation_file = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None

        if not Path(temp_file).exists():
            print(f"Error: Temp file not found: {temp_file}")
            sys.exit(1)

        if not Path(translation_file).exists():
            print(f"Error: Translation file not found: {translation_file}")
            sys.exit(1)

        save_and_generate(temp_file, translation_file, output_dir)


if __name__ == '__main__':
    main()
