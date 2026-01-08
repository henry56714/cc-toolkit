#!/usr/bin/env python3
"""
单词翻译缓存管理器

功能：
1. 查询已翻译的单词，避免重复翻译
2. 保存新翻译的单词到缓存
3. 确保缓存中不存在重复单词
4. 提供批量查询和更新接口
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class TranslationCache:
    """单词翻译缓存管理器"""

    def __init__(self, cache_file: str = None):
        """
        初始化缓存管理器

        Args:
            cache_file: 缓存文件路径，默认为 skill 目录下的 translation_cache.json
        """
        if cache_file is None:
            # 默认路径：skill 目录下的 translation_cache.json
            script_dir = Path(__file__).parent
            skill_dir = script_dir.parent
            cache_file = skill_dir / 'translation_cache.json'

        self.cache_file = Path(cache_file)
        self.cache: Dict[str, dict] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """从文件加载缓存"""
        if self.cache_file.exists():
            try:
                content = self.cache_file.read_text(encoding='utf-8')
                self.cache = json.loads(content)
            except Exception as e:
                print(f"Warning: Failed to load cache file: {e}")
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self) -> None:
        """保存缓存到文件"""
        try:
            content = json.dumps(self.cache, ensure_ascii=False, indent=2)
            self.cache_file.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Error: Failed to save cache file: {e}")

    def get(self, word: str) -> Optional[dict]:
        """
        查询单词翻译

        Args:
            word: 单词（小写）

        Returns:
            翻译信息字典，如果不存在则返回 None
            格式：{
                'translation': 'n. 驼背；隆起',
                'sentence_examples': [
                    {
                        'sentence': 'So does he have a hump?',
                        'sentence_translation': '那他有驼背吗？'
                    }
                ]
            }
        """
        word_lower = word.lower()
        return self.cache.get(word_lower)

    def add(self, word: str, translation: str,
            sentence: str = '', sentence_translation: str = '') -> None:
        """
        添加或更新单词翻译

        Args:
            word: 单词
            translation: 中文翻译（包含词性）
            sentence: 例句（可选）
            sentence_translation: 例句翻译（可选）
        """
        word_lower = word.lower()

        # 如果单词已存在，更新翻译并添加新的例句
        if word_lower in self.cache:
            # 更新翻译（保留最新的翻译）
            self.cache[word_lower]['translation'] = translation

            # 添加例句（如果提供了且不重复）
            if sentence and sentence_translation:
                example = {
                    'sentence': sentence,
                    'sentence_translation': sentence_translation
                }

                # 检查是否已存在相同例句
                examples = self.cache[word_lower].get('sentence_examples', [])
                if example not in examples:
                    examples.append(example)
                    self.cache[word_lower]['sentence_examples'] = examples
        else:
            # 新增单词
            self.cache[word_lower] = {
                'translation': translation,
                'sentence_examples': []
            }

            if sentence and sentence_translation:
                self.cache[word_lower]['sentence_examples'].append({
                    'sentence': sentence,
                    'sentence_translation': sentence_translation
                })

        self._save_cache()

    def batch_get(self, words: List[str]) -> Dict[str, dict]:
        """
        批量查询单词翻译

        Args:
            words: 单词列表

        Returns:
            字典，key 为单词，value 为翻译信息（如果存在）
        """
        result = {}
        for word in words:
            word_lower = word.lower()
            translation = self.get(word_lower)
            if translation:
                result[word_lower] = translation
        return result

    def batch_add(self, word_data: List[dict]) -> None:
        """
        批量添加单词翻译

        Args:
            word_data: 单词数据列表，每个元素包含：
                {
                    'word': '单词',
                    'translation': '翻译',
                    'sentence': '例句',
                    'sentence_translation': '例句翻译'
                }
        """
        for item in word_data:
            self.add(
                word=item['word'],
                translation=item.get('translation', ''),
                sentence=item.get('sentence', ''),
                sentence_translation=item.get('sentence_translation', '')
            )

    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        total_words = len(self.cache)
        total_examples = sum(
            len(word_data.get('sentence_examples', []))
            for word_data in self.cache.values()
        )
        return {
            'total_words': total_words,
            'total_examples': total_examples
        }

    def clear(self) -> None:
        """清空缓存（谨慎使用）"""
        self.cache = {}
        self._save_cache()


def main():
    """命令行工具：查询和管理翻译缓存"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python translation_cache.py stats              # 查看缓存统计")
        print("  python translation_cache.py get <word>         # 查询单词")
        print("  python translation_cache.py add <word> <translation> [sentence] [sentence_translation]")
        sys.exit(1)

    cache = TranslationCache()
    command = sys.argv[1]

    if command == 'stats':
        stats = cache.get_stats()
        print(f"Total words: {stats['total_words']}")
        print(f"Total examples: {stats['total_examples']}")

    elif command == 'get':
        if len(sys.argv) < 3:
            print("Error: word required")
            sys.exit(1)

        word = sys.argv[2]
        result = cache.get(word)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Word '{word}' not found in cache")

    elif command == 'add':
        if len(sys.argv) < 4:
            print("Error: word and translation required")
            sys.exit(1)

        word = sys.argv[2]
        translation = sys.argv[3]
        sentence = sys.argv[4] if len(sys.argv) > 4 else ''
        sentence_translation = sys.argv[5] if len(sys.argv) > 5 else ''

        cache.add(word, translation, sentence, sentence_translation)
        print(f"Added/updated word: {word}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
