"""
Image Viewer

图片查看器，支持缩略图列表和放大查看。
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QLabel, QScrollArea, QPushButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage
import os


class ImageViewer(QDialog):
    """图片查看器"""

    def __init__(self, image_paths, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.current_index = 0
        self.setWindowTitle("图片查看器")
        self.resize(1200, 800)
        self.setup_ui()
        if image_paths:
            self.show_image(0)

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # 左侧缩略图列表
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setIconSize(QSize(150, 150))
        self.thumbnail_list.setMaximumWidth(180)
        self.thumbnail_list.currentRowChanged.connect(self.show_image)

        for path in self.image_paths:
            item = QListWidgetItem(os.path.basename(path))
            pixmap = QPixmap(path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
            self.thumbnail_list.addItem(item)

        layout.addWidget(self.thumbnail_list)

        # 右侧大图显示
        right_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.image_label)
        right_layout.addWidget(scroll)

        # 按钮
        btn_layout = QHBoxLayout()
        prev_btn = QPushButton("上一张")
        prev_btn.clicked.connect(self.prev_image)
        next_btn = QPushButton("下一张")
        next_btn.clicked.connect(self.next_image)
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        right_layout.addLayout(btn_layout)

        layout.addLayout(right_layout, 1)

    def show_image(self, index):
        if 0 <= index < len(self.image_paths):
            self.current_index = index
            pixmap = QPixmap(self.image_paths[index])
            self.image_label.setPixmap(pixmap)

    def prev_image(self):
        if self.current_index > 0:
            self.thumbnail_list.setCurrentRow(self.current_index - 1)

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.thumbnail_list.setCurrentRow(self.current_index + 1)
