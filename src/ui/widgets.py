from PySide6.QtWidgets import (
    QPushButton,
    QLabel,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
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


class DropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setMinimumHeight(180)
        self.setMinimumWidth(300)
        self.setAcceptDrops(True)
        self.is_hovering = False

        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(79, 195, 247, 12);
                border-radius: 12px;
                padding: 6px;
                margin: 0px;
            }
        """)
        if HAS_QTAWESOME:
            pixmap = qta.icon("fa5s.cloud-upload-alt", color="#4FC3F7").pixmap(32, 32)
            self.icon_label.setPixmap(pixmap)
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.title_label = QLabel("Drop here or click to browse")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 13px;
                font-weight: 500;
                background-color: rgba(79, 195, 247, 8);
                border-radius: 8px;
                padding: 6px 16px;
                margin: 0px;
            }
        """)
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.sub_label = QLabel(
            "Supports XML and PNG files or folders containing XML and PNG files"
        )
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("""
            QLabel {
                color: #78909C;
                font-size: 11px;
                background-color: rgba(79, 195, 247, 6);
                border-radius: 6px;
                padding: 4px 14px;
                margin: 0px;
            }
        """)
        layout.addWidget(self.sub_label, alignment=Qt.AlignCenter)

        self.update_style(False)

    def update_style(self, hovering):
        if hovering:
            self.setStyleSheet(f"""
                QWidget {{
                    background: rgba(79, 195, 247, 10);
                    border: 2px solid rgba(79, 195, 247, 50);
                    border-radius: 14px;
                }}
            """)

            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(79, 195, 247, 25);
                    border-radius: 12px;
                    padding: 6px;
                    margin: 0px;
                }
            """)
            if HAS_QTAWESOME:
                pixmap = qta.icon("fa5s.cloud-upload-alt", color="#64D8FF").pixmap(
                    32, 32
                )
                self.icon_label.setPixmap(pixmap)

            self.title_label.setStyleSheet("""
                QLabel {
                    color: #4FC3F7;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: rgba(79, 195, 247, 18);
                    border-radius: 8px;
                    padding: 6px 16px;
                    margin: 0px;
                }
            """)

            self.sub_label.setStyleSheet("""
                QLabel {
                    color: #90A4AE;
                    font-size: 11px;
                    background-color: rgba(79, 195, 247, 14);
                    border-radius: 6px;
                    padding: 4px 14px;
                    margin: 0px;
                }
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background: rgba(26, 35, 70, 30);
                    border: 2px dashed rgba(79, 195, 247, 15);
                    border-radius: 14px;
                }}
            """)

            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(79, 195, 247, 12);
                    border-radius: 12px;
                    padding: 6px;
                    margin: 0px;
                }
            """)
            if HAS_QTAWESOME:
                pixmap = qta.icon("fa5s.cloud-upload-alt", color="#4FC3F7").pixmap(
                    32, 32
                )
                self.icon_label.setPixmap(pixmap)

            self.title_label.setStyleSheet("""
                QLabel {
                    color: #E0E0E0;
                    font-size: 13px;
                    font-weight: 500;
                    background-color: rgba(79, 195, 247, 8);
                    border-radius: 8px;
                    padding: 6px 16px;
                    margin: 0px;
                }
            """)

            self.sub_label.setStyleSheet("""
                QLabel {
                    color: #78909C;
                    font-size: 11px;
                    background-color: rgba(79, 195, 247, 6);
                    border-radius: 6px;
                    padding: 4px 14px;
                    margin: 0px;
                }
            """)

    def enterEvent(self, event):
        if hasattr(event, "mimeData"):
            if event.mimeData().hasUrls():
                self.is_hovering = True
                self.update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_hovering:
            self.update_style(False)
        super().leaveEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.is_hovering = True
            self.update_style(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.is_hovering = False
        self.update_style(False)
        event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.is_hovering = False
        self.update_style(False)

        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)

        if files and self.parent_window:
            self.parent_window.process_dropped_files(files)
            event.acceptProposedAction()
        else:
            event.ignore()
