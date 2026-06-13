"""
Main Window Module

主窗口 UI，提供图片选择、翻译和结果显示功能。
"""

import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit,
    QFileDialog, QMessageBox, QDialog, QLineEdit,
    QFormLayout, QDialogButtonBox, QGroupBox, QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QPixmap, QImage

from ui.api_client import APIClient
from ui.image_viewer import ImageViewer
from ui.start_page import StartPage
from ui.translate_page import TranslatePage
from ui.detail_page import DetailPage
from core.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """设置对话框，用于配置百度翻译 API 密钥。"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """设置 UI。"""
        layout = QFormLayout()

        # 百度 API 配置
        api_group = QGroupBox("百度翻译 API 配置")
        api_layout = QFormLayout()

        self.app_id_input = QLineEdit()
        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)

        # 加载现有配置
        app_id, secret = self.config_manager.get_baidu_credentials()
        self.app_id_input.setText(app_id)
        self.secret_input.setText(secret)

        api_layout.addRow("APP ID:", self.app_id_input)
        api_layout.addRow("密钥:", self.secret_input)

        api_group.setLayout(api_layout)
        layout.addRow(api_group)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def accept(self):
        """保存设置。"""
        app_id = self.app_id_input.text().strip()
        secret = self.secret_input.text().strip()

        if not app_id or not secret:
            QMessageBox.warning(self, "警告", "请填写完整的 API 配置信息")
            return

        self.config_manager.set_baidu_credentials(app_id, secret)

        # 立即更新环境变量
        os.environ["BAIDU_APP_ID"] = app_id
        os.environ["BAIDU_SECRET_KEY"] = secret

        super().accept()


class MainWindow(QMainWindow):
    """主窗口 - 页面切换"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.api_client = APIClient()
        self.setup_ui()
        self.check_api_config()

    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("漫画翻译器 - 日译中")
        self.setMinimumSize(1200, 800)

        # 页面切换
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 首页
        self.start_page = StartPage(self.config_manager)
        self.start_page.images_selected.connect(self.on_images_selected)
        self.stacked_widget.addWidget(self.start_page)

        # 翻译页面
        self.translate_page = TranslatePage(self.config_manager, self.api_client)
        self.translate_page.back_requested.connect(self.show_start_page)
        self.translate_page.detail_requested.connect(self.show_detail_page)
        self.stacked_widget.addWidget(self.translate_page)

        # 详细查看页面
        self.detail_page = DetailPage()
        self.detail_page.back_requested.connect(self.show_translate_page)
        self.stacked_widget.addWidget(self.detail_page)

    def on_images_selected(self, image_paths):
        """图片选择完成，跳转到翻译页面"""
        self.translate_page.load_images(image_paths)
        self.stacked_widget.setCurrentWidget(self.translate_page)

    def show_start_page(self):
        """返回首页"""
        self.stacked_widget.setCurrentWidget(self.start_page)

    def show_translate_page(self):
        """显示翻译页面"""
        self.stacked_widget.setCurrentWidget(self.translate_page)

    def show_detail_page(self, image_path):
        """显示详细查看页面"""
        self.detail_page.show_image(image_path)
        self.stacked_widget.setCurrentWidget(self.detail_page)

    def check_api_config(self):
        """检查 API 配置"""
        if not self.config_manager.has_baidu_credentials():
            QMessageBox.information(
                self,
                "首次使用",
                "欢迎使用漫画翻译器！\n\n请先配置百度翻译 API 密钥。\n点击确定后将打开设置窗口。"
            )
            self.open_settings()

    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        dialog.exec()
