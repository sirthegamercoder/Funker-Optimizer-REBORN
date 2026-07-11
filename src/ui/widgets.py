from PySide6.QtWidgets import QPushButton, QLabel, QCheckBox, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QPen, QFont

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


class ModernCheckBox(QCheckBox):
    def __init__(self, text, parent=None, checked=False):
        super().__init__(text, parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(30)
        self._hover = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRect(0, 4, 22, 22)

        if self.isChecked():
            border_color = QColor("#4FC3F7")
        else:
            border_color = QColor("#2C3E6B")

        if self._hover and not self.isChecked():
            border_color = QColor("#4FC3F7")

        bg_color = QColor(26, 35, 126, 50)

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, 6, 6)

        if self.isChecked() and HAS_QTAWESOME:
            icon = qta.icon("fa5s.check", color="#4FC3F7")
            icon.paint(painter, rect, Qt.AlignCenter)
        elif self.isChecked():
            painter.setPen(QPen(QColor("#4FC3F7"), 2))
            painter.drawLine(6, 14, 9, 18)
            painter.drawLine(9, 18, 16, 8)

        text_rect = QRect(30, 0, self.width() - 30, self.height())
        painter.setPen(QColor("#B0BEC5"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Normal))
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

        painter.end()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def hitButton(self, pos):
        return True
