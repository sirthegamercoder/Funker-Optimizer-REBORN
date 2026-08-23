import sys
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

from ui.main_window import FunkerOptimizerREBORN


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    screen_splash = QPixmap(":/images/for-splash.png")
    intro_screen = QSplashScreen(screen_splash)
    intro_screen.show()
    app.processEvents()

    for i in range(1 + 1):
        progress = int((i) * 100)

        message = f"{progress}%"

        intro_screen.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()

        time.sleep(0.3 + (0.1 if i % 2 == 0 else 0))

    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setWindowIcon(QIcon(":/images/icon.ico"))

    window = FunkerOptimizerREBORN()
    window.show()
    intro_screen.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
