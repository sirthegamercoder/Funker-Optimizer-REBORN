from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QPoint
from PySide6.QtGui import QColor

from core.constants import COLOR_PRIMARY

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False


class ModernButton(QPushButton):
    def __init__(self, text, icon=None, icon_color=COLOR_PRIMARY, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)

        if icon and HAS_QTAWESOME:
            self.setIcon(qta.icon(icon, color=icon_color))
            self.setIconSize(QSize(20, 20))

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(79, 195, 247, 40))
        self.shadow.setOffset(0, 5)
        self.setGraphicsEffect(self.shadow)

        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        self.offset_anim = QPropertyAnimation(self.shadow, b"offset")
        self.offset_anim.setDuration(250)
        self.offset_anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self.anim.setEndValue(30)
        self.anim.start()
        self.offset_anim.setEndValue(QPoint(0, 8))
        self.offset_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setEndValue(20)
        self.anim.start()
        self.offset_anim.setEndValue(QPoint(0, 5))
        self.offset_anim.start()
        super().leaveEvent(event)


class IconLabel(QLabel):
    def __init__(self, icon, color=COLOR_PRIMARY, size=20, parent=None):
        super().__init__(parent)
        if HAS_QTAWESOME:
            self.setPixmap(qta.icon(icon, color=color).pixmap(size, size))
        self.setFixedSize(size + 16, size + 16)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(79, 195, 247, 12);
                border-radius: 8px;
                padding: 4px;
                margin: 0px;
            }
        """)