from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent


class ZoomableLabel(QLabel):
    """支持缩放和拖动的图片标签"""

    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.drag_start = None
        self.setMouseTracking(True)

    def set_pixmap(self, pixmap):
        """设置图片"""
        self.pixmap = pixmap
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.update()

    def paintEvent(self, event):
        """绘制图片"""
        if not self.pixmap:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        scaled_size = self.pixmap.size() * self.scale
        x = (self.width() - scaled_size.width()) // 2 + self.offset.x()
        y = (self.height() - scaled_size.height()) // 2 + self.offset.y()

        painter.drawPixmap(x, y, scaled_size.width(), scaled_size.height(), self.pixmap)

    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放"""
        if not self.pixmap:
            return

        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        self.scale *= factor
        self.scale = max(0.1, min(self.scale, 10.0))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动拖动图片"""
        if self.drag_start:
            delta = event.pos() - self.drag_start
            self.offset += delta
            self.drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)


class DetailPage(QWidget):
    """图片详细查看页面"""
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 顶部返回按钮
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← 返回")
        back_btn.clicked.connect(self.back_requested.emit)
        back_btn.setFixedWidth(100)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 图片显示区域
        self.image_label = ZoomableLabel()
        self.image_label.setStyleSheet("background: #f0f0f0;")
        layout.addWidget(self.image_label)

    def show_image(self, image_path):
        """显示单张图片"""
        pixmap = QPixmap(image_path)
        self.image_label.set_pixmap(pixmap)
