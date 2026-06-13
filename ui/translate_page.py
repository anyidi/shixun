"""
Translate Page - 翻译页面
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                              QListWidget, QListWidgetItem, QGroupBox, QComboBox, QTextEdit,
                              QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap


class TranslatorThread(QThread):
    """翻译线程"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str, str)

    def __init__(self, api_client, input_path, use_gpu=True):
        super().__init__()
        self.api_client = api_client
        self.input_path = input_path
        self.use_gpu = use_gpu

    def run(self):
        self.status_updated.emit("正在翻译...")
        success, result_path, error = self.api_client.translate(self.input_path, self.use_gpu)
        self.finished.emit(success, result_path, error)


class BatchTranslatorThread(QThread):
    """批量翻译线程"""
    progress_updated = pyqtSignal(int, int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, api_client, input_paths, use_gpu=True):
        super().__init__()
        self.api_client = api_client
        self.input_paths = input_paths
        self.use_gpu = use_gpu

    def run(self):
        results = {}
        total = len(self.input_paths)
        for i, path in enumerate(self.input_paths):
            self.status_updated.emit(f"正在翻译 {i+1}/{total}: {os.path.basename(path)}")
            self.progress_updated.emit(i+1, total)
            success, result_path, error = self.api_client.translate(path, self.use_gpu)
            if success:
                results[path] = result_path
        self.finished.emit(results)


class TranslatePage(QWidget):
    """翻译页面"""

    back_requested = pyqtSignal()
    detail_requested = pyqtSignal(str)

    def __init__(self, config_manager, api_client):
        super().__init__()
        self.config_manager = config_manager
        self.api_client = api_client
        self.image_paths = []
        self.current_index = 0
        self.result_paths = {}
        self.translator_thread = None
        self.batch_thread = None
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # 左侧：图片列表
        left_layout = QVBoxLayout()

        back_btn = QPushButton("← 返回")
        back_btn.clicked.connect(self.back_requested.emit)
        left_layout.addWidget(back_btn)

        list_group = QGroupBox("已选图片")
        list_layout = QVBoxLayout()
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.currentRowChanged.connect(self.on_image_selected)
        list_layout.addWidget(self.image_list)
        list_group.setLayout(list_layout)
        left_layout.addWidget(list_group)

        layout.addLayout(left_layout)

        # 中间：图片显示
        center_layout = QVBoxLayout()

        images_layout = QHBoxLayout()

        original_group = QGroupBox("原图")
        original_layout = QVBoxLayout()
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setMinimumSize(350, 500)
        self.original_label.setStyleSheet("background: white; border: 2px solid #dee2e6; border-radius: 8px;")
        original_layout.addWidget(self.original_label)
        detail_original_btn = QPushButton("查看大图")
        detail_original_btn.clicked.connect(self.show_original_detail)
        original_layout.addWidget(detail_original_btn)
        original_group.setLayout(original_layout)

        result_group = QGroupBox("翻译结果")
        result_layout = QVBoxLayout()
        self.result_label = QLabel("未翻译")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setMinimumSize(350, 500)
        self.result_label.setStyleSheet("background: white; border: 2px solid #dee2e6; border-radius: 8px;")
        result_layout.addWidget(self.result_label)
        detail_result_btn = QPushButton("查看大图")
        detail_result_btn.clicked.connect(self.show_result_detail)
        result_layout.addWidget(detail_result_btn)
        result_group.setLayout(result_layout)

        images_layout.addWidget(original_group)
        images_layout.addWidget(result_group)
        center_layout.addLayout(images_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(20)
        center_layout.addWidget(self.progress_bar)

        # 日志
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        center_layout.addWidget(log_group)

        layout.addLayout(center_layout)

        # 右侧：翻译器选择
        right_layout = QVBoxLayout()

        translator_group = QGroupBox("翻译设置")
        translator_layout = QVBoxLayout()

        translator_layout.addWidget(QLabel("翻译引擎:"))
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(["百度翻译"])
        translator_layout.addWidget(self.translator_combo)

        translator_layout.addSpacing(20)

        self.translate_btn = QPushButton("翻译当前图片")
        self.translate_btn.setMinimumHeight(50)
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #5b7dff;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4a6de5;
            }
        """)
        self.translate_btn.clicked.connect(self.translate_current)
        translator_layout.addWidget(self.translate_btn)

        self.translate_all_btn = QPushButton("翻译全部")
        self.translate_all_btn.setMinimumHeight(50)
        self.translate_all_btn.clicked.connect(self.translate_all)
        translator_layout.addWidget(self.translate_all_btn)

        translator_layout.addStretch()
        translator_group.setLayout(translator_layout)
        right_layout.addWidget(translator_group)

        layout.addLayout(right_layout)

    def load_images(self, image_paths):
        """加载图片列表"""
        self.image_paths = image_paths
        self.result_paths = {}
        self.image_list.clear()

        for path in image_paths:
            item = QListWidgetItem(os.path.basename(path))
            pixmap = QPixmap(path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
            self.image_list.addItem(item)

        if image_paths:
            self.image_list.setCurrentRow(0)

    def on_image_selected(self, index):
        """选择图片"""
        if 0 <= index < len(self.image_paths):
            self.current_index = index
            path = self.image_paths[index]
            pixmap = QPixmap(path)
            self.original_label.setPixmap(pixmap.scaled(self.original_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

            # 显示翻译结果（如果有）
            if path in self.result_paths:
                result_pixmap = QPixmap(self.result_paths[path])
                self.result_label.setPixmap(result_pixmap.scaled(self.result_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.result_label.setText("未翻译")
                self.result_label.setPixmap(QPixmap())

    def translate_current(self):
        """翻译当前图片"""
        if not self.image_paths:
            return

        current_path = self.image_paths[self.current_index]
        self.log(f"开始翻译: {os.path.basename(current_path)}")

        self.translate_btn.setEnabled(False)
        use_gpu = self.config_manager.get("use_gpu", True)

        self.translator_thread = TranslatorThread(self.api_client, current_path, use_gpu)
        self.translator_thread.status_updated.connect(self.log)
        self.translator_thread.finished.connect(self.on_translate_finished)
        self.translator_thread.start()

    def translate_all(self):
        """翻译全部图片"""
        if not self.image_paths:
            return

        self.translate_btn.setEnabled(False)
        self.translate_all_btn.setEnabled(False)
        self.log(f"开始批量翻译 {len(self.image_paths)} 张图片")

        use_gpu = self.config_manager.get("use_gpu", True)
        self.batch_thread = BatchTranslatorThread(self.api_client, self.image_paths, use_gpu)
        self.batch_thread.status_updated.connect(self.log)
        self.batch_thread.progress_updated.connect(self.on_batch_progress)
        self.batch_thread.finished.connect(self.on_batch_finished)
        self.batch_thread.start()

    def on_batch_progress(self, current, total):
        """批量翻译进度"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)

    def on_batch_finished(self, results):
        """批量翻译完成"""
        self.translate_btn.setEnabled(True)
        self.translate_all_btn.setEnabled(True)
        self.progress_bar.setValue(0)

        self.result_paths.update(results)
        self.log(f"✓ 批量翻译完成！成功 {len(results)}/{len(self.image_paths)} 张")

        # 刷新当前显示
        if self.image_paths and self.current_index < len(self.image_paths):
            current_path = self.image_paths[self.current_index]
            if current_path in self.result_paths:
                result_pixmap = QPixmap(self.result_paths[current_path])
                self.result_label.setPixmap(result_pixmap)
                self.result_label.adjustSize()

        QMessageBox.information(self, "完成", f"批量翻译完成！\n成功: {len(results)}\n失败: {len(self.image_paths)-len(results)}")

    def on_translate_finished(self, success, result_path, error):
        """翻译完成"""
        self.translate_btn.setEnabled(True)

        if success:
            current_path = self.image_paths[self.current_index]
            self.result_paths[current_path] = result_path

            result_pixmap = QPixmap(result_path)
            self.result_label.setPixmap(result_pixmap.scaled(self.result_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
            self.log("✓ 翻译完成")
        else:
            self.log(f"✗ 翻译失败: {error}")
            QMessageBox.critical(self, "错误", f"翻译失败:\n{error}")

    def show_original_detail(self):
        """查看原图大图"""
        if 0 <= self.current_index < len(self.image_paths):
            original_path = self.image_paths[self.current_index]
            self.detail_requested.emit(original_path)

    def show_result_detail(self):
        """查看翻译结果大图"""
        if 0 <= self.current_index < len(self.image_paths):
            original_path = self.image_paths[self.current_index]
            result_path = self.result_paths.get(original_path)
            if result_path:
                self.detail_requested.emit(result_path)
            else:
                QMessageBox.information(self, "提示", "当前图片尚未翻译")

    def log(self, message):
        """添加日志"""
        self.log_text.append(message)
