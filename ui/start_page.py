"""
Start Page - 首页选择图片
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class StartPage(QWidget):
    """首页 - 选择图片或文件夹"""

    images_selected = pyqtSignal(list)  # 选择完成信号

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标题
        title = QLabel("漫画翻译器 - 日译中")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(50)

        # 按钮
        btn_layout = QHBoxLayout()

        select_image_btn = QPushButton("选择图片")
        select_image_btn.setMinimumSize(200, 80)
        select_image_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #5b7dff;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #4a6de5;
            }
        """)
        select_image_btn.clicked.connect(self.select_image)

        select_folder_btn = QPushButton("选择文件夹")
        select_folder_btn.setMinimumSize(200, 80)
        select_folder_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #5b7dff;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #4a6de5;
            }
        """)
        select_folder_btn.clicked.connect(self.select_folder)

        btn_layout.addWidget(select_image_btn)
        btn_layout.addSpacing(30)
        btn_layout.addWidget(select_folder_btn)

        layout.addLayout(btn_layout)

    def select_image(self):
        """选择单张图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择漫画图片",
            self.config_manager.get("last_input_dir", ""),
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.config_manager.set("last_input_dir", os.path.dirname(file_path))
            self.config_manager.save_config()
            self.images_selected.emit([file_path])

    def select_folder(self):
        """选择文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            self.config_manager.get("last_input_dir", "")
        )

        if folder_path:
            exts = ('.png', '.jpg', '.jpeg', '.bmp')
            image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                          if f.lower().endswith(exts)]
            image_paths.sort()

            if not image_paths:
                QMessageBox.warning(self, "警告", "文件夹中没有图片文件")
                return

            self.config_manager.set("last_input_dir", folder_path)
            self.config_manager.save_config()
            self.images_selected.emit(image_paths)
