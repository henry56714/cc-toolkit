#!/usr/bin/env python3
"""
配置管理模块

读取 config.json 配置文件，提供配置访问函数。
"""

import json
from pathlib import Path


def get_config_path() -> Path:
    """获取配置文件路径"""
    return Path(__file__).parent.parent / 'config.json'


def load_config() -> dict:
    """
    加载配置文件

    Returns:
        配置字典，如果配置文件不存在则返回空字典
    """
    config_path = get_config_path()

    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError):
            return {}

    return {}


def get_output_dir() -> Path:
    """
    获取 Anki 文件输出目录

    Returns:
        输出目录的 Path 对象
        - 如果配置了 output_dir，返回配置的目录（自动展开 ~）
        - 否则返回当前工作目录
    """
    config = load_config()
    output_dir = config.get('output_dir')

    if output_dir:
        # 展开 ~ 为用户主目录
        path = Path(output_dir).expanduser()
        # 确保目录存在
        path.mkdir(parents=True, exist_ok=True)
        return path

    return Path.cwd()
