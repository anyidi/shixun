"""
Configuration Manager Module

管理应用配置，包括百度翻译 API 密钥的存储和读取。
"""

import os
import json
from typing import Optional, Dict


class ConfigManager:
    """
    配置管理器，负责读取和保存应用配置。
    """

    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器。

        Args:
            config_dir: 配置目录路径，默认使用用户主目录下的 .manga_translator
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".manga_translator")

        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

        # 默认配置
        self.default_config = {
            "baidu_app_id": "",
            "baidu_secret_key": "",
            "use_gpu": True,
            "last_input_dir": "",
            "last_output_dir": ""
        }

        # 加载配置
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """
        从文件加载配置。

        Returns:
            配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置（处理新增字段）
                    return {**self.default_config, **config}
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()

    def save_config(self) -> bool:
        """
        保存配置到文件。

        Returns:
            是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key: str, default=None):
        """
        获取配置项。

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self.config.get(key, default)

    def set(self, key: str, value):
        """
        设置配置项。

        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value

    def get_baidu_credentials(self) -> tuple[str, str]:
        """
        获取百度翻译 API 凭据。

        Returns:
            (app_id, secret_key)
        """
        app_id = self.config.get("baidu_app_id", "")
        secret = self.config.get("baidu_secret_key", "")
        return app_id, secret

    def set_baidu_credentials(self, app_id: str, secret_key: str):
        """
        设置百度翻译 API 凭据。

        Args:
            app_id: APP ID
            secret_key: 密钥
        """
        self.config["baidu_app_id"] = app_id
        self.config["baidu_secret_key"] = secret_key
        self.save_config()

    def has_baidu_credentials(self) -> bool:
        """
        检查是否已配置百度翻译 API 凭据。

        Returns:
            是否已配置
        """
        app_id, secret = self.get_baidu_credentials()
        return bool(app_id and secret)
