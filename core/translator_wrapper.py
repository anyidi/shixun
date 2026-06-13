"""
Translator Wrapper Module

封装 manga-image-translator 的核心翻译功能，
提供简单的同步接口供 PyQt6 应用使用。
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Optional, Tuple

# 添加 manga-image-translator 到 Python 路径
MANGA_TRANSLATOR_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "manga-image-translator")
if MANGA_TRANSLATOR_PATH not in sys.path:
    sys.path.insert(0, MANGA_TRANSLATOR_PATH)

from manga_translator import Config
# 注意：不在这里导入 MangaTranslatorLocal，而是在设置环境变量后动态导入
# from manga_translator.mode.local import MangaTranslatorLocal


class TranslatorWrapper:
    """
    封装 MangaTranslatorLocal，提供简单的翻译接口。
    """

    def __init__(self, config_path: str = None, baidu_app_id: str = None, baidu_secret: str = None):
        """
        初始化翻译器。

        Args:
            config_path: 配置文件路径，默认使用 config.json
            baidu_app_id: 百度翻译 APP ID
            baidu_secret: 百度翻译密钥
        """
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.baidu_app_id = baidu_app_id
        self.baidu_secret = baidu_secret

        # 设置环境变量
        if baidu_app_id:
            os.environ["BAIDU_APP_ID"] = baidu_app_id
        if baidu_secret:
            os.environ["BAIDU_SECRET_KEY"] = baidu_secret

        self.result_dir = os.path.join(MANGA_TRANSLATOR_PATH, "result")
        os.makedirs(self.result_dir, exist_ok=True)

        # 进度回调
        self.progress_callback = None
        self.status_callback = None

    def set_progress_callback(self, callback):
        """设置进度回调函数。"""
        self.progress_callback = callback

    def set_status_callback(self, callback):
        """设置状态回调函数。"""
        self.status_callback = callback

    def _safe_progress_update(self, value):
        """安全的进度更新，确保值为整数。"""
        if self.progress_callback and value is not None:
            try:
                self.progress_callback(int(value))
            except (ValueError, TypeError):
                pass

    def _safe_status_update(self, message):
        """安全的状态更新。"""
        if self.status_callback and message:
            try:
                self.status_callback(str(message))
            except Exception:
                pass

    def translate_image(self, input_path: str, use_gpu: bool = True) -> Tuple[bool, str, str]:
        """同步翻译（用于非 async 环境）"""
        return asyncio.run(self.translate_image_async(input_path, use_gpu))

    async def translate_image_async(self, input_path: str, use_gpu: bool = True) -> Tuple[bool, str, str]:
        """
        翻译单张图片。

        Args:
            input_path: 输入图片路径
            use_gpu: 是否使用 GPU

        Returns:
            (success, result_path, error_message)
        """
        try:
            # 验证输入文件
            if not os.path.exists(input_path):
                return False, "", f"文件不存在: {input_path}"

            self._safe_status_update("正在加载配置...")

            # 加载配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            config = Config(**config_dict)

            # 检查环境变量（已在主窗口初始化时设置）
            if not os.environ.get("BAIDU_APP_ID") or not os.environ.get("BAIDU_SECRET_KEY"):
                return False, "", "未配置百度翻译 API 密钥，请在设置中配置"

            self._safe_status_update("正在初始化翻译器...")

            # 导入 MangaTranslatorLocal（环境变量已在应用启动时设置）
            from manga_translator.mode.local import MangaTranslatorLocal

            # 准备参数（完全按照原项目的argparse参数）
            params = {
                "use_gpu": use_gpu,
                "verbose": True,
                "overwrite": True,
                "attempts": 0,  # 默认0，与原项目一致
                "kernel_size": 3,  # 默认3，与原项目一致
                "ignore_errors": False,
                "mode": "local",
                "config_file": self.config_path  # 传递配置文件路径
            }

            # 创建翻译器实例
            translator = MangaTranslatorLocal(params)

            # 输出路径 - 使用输入文件名避免覆盖
            input_filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.result_dir, f"{input_filename}_translated.png")

            self._safe_status_update("正在翻译图片...")
            self._safe_progress_update(10)

            # 运行翻译
            await self._translate_async(translator, input_path, output_path, params)

            self._safe_progress_update(100)
            self._safe_status_update("翻译完成！")

            # 检查结果文件
            if os.path.exists(output_path):
                return True, output_path, ""
            else:
                return False, "", "翻译失败：未生成输出文件"

        except Exception as e:
            import traceback
            error_msg = f"翻译出错: {str(e)}\n详细信息:\n{traceback.format_exc()}"
            self._safe_status_update(error_msg)
            return False, "", error_msg

    async def _translate_async(self, translator,
                               input_path: str, output_path: str, params: dict):
        """
        异步翻译方法。
        """
        self._safe_progress_update(20)

        await translator.translate_path(input_path, output_path, params)

        self._safe_progress_update(90)
