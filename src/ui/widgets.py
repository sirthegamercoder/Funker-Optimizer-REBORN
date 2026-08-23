from PySide6.QtWidgets import QPushButton, QLabel, QCheckBox, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QPen, QFont

try:
    import qtawesome as qta

    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False


class ModernButton(QPushButton):
    def __init__(self, text, icon=None, icon_color="#4FC3F7", parent=None):
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
    def __init__(self, icon, color="#4FC3F7", size=20, parent=None):
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
        self.setFixedHeight(34)
        self._hover = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRect(0, 6, 22, 22)

        if self.isChecked():
            border_color = QColor("#4FC3F7")
            bg_color = QColor(79, 195, 247, 40)
        else:
            border_color = QColor("#3A4E8B")
            bg_color = QColor(26, 35, 70, 80)

        if self._hover and not self.isChecked():
            border_color = QColor("#4FC3F7")
            bg_color = QColor(79, 195, 247, 20)

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, 6, 6)

        if self.isChecked() and HAS_QTAWESOME:
            icon = qta.icon("fa5s.check", color="#4FC3F7")
            icon.paint(painter, rect, Qt.AlignCenter)
        elif self.isChecked():
            painter.setPen(QPen(QColor("#4FC3F7"), 2.5))
            painter.drawLine(6, 16, 10, 20)
            painter.drawLine(10, 20, 18, 10)

        text_rect = QRect(30, 2, self.width() - 30, self.height())

        painter.setPen(QColor("#E0E0E0"))
        painter.setFont(
            QFont("Segoe UI", 12, QFont.Bold if self.isChecked() else QFont.Normal)
        )
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


class RemoveButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("X", parent)
        self.setFixedSize(20, 20)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 82, 82, 20);
                color: #FF5252;
                border: 1px solid rgba(255, 82, 82, 40);
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 82, 82, 60);
                color: #FFFFFF;
                border-color: #FF5252;
            }
            QPushButton:pressed {
                background-color: rgba(255, 82, 82, 90);
            }
        """)
