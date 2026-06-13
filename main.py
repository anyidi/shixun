"""
Manga Translator Desktop Application

漫画翻译器桌面应用 - 日译中
使用 PyQt6 和 manga-image-translator 核心库
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def load_stylesheet(app):
    """加载样式表。"""
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())


def main():
    """应用入口函数。"""
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("漫画翻译器")
    app.setOrganizationName("MangaTranslator")

    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 加载样式
    load_stylesheet(app)

    # 创建主窗口
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
