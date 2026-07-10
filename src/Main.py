import sys
import os
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

from core.constants import APP_NAME, RESOURCE_PATH
from ui.main_window import FunkerOptimizerREBORN


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    splash_path = RESOURCE_PATH("src/assets/for-splash.png")
    screen_splash = QPixmap(str(splash_path))
    intro_screen = QSplashScreen(screen_splash)
    intro_screen.show()
    app.processEvents()

    for i in range(1, 6):
        intro_screen.showMessage(
            f"{i*20}% loading", Qt.AlignBottom | Qt.AlignCenter, Qt.white
        )
        app.processEvents()
        time.sleep(0.6)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    icon_path = RESOURCE_PATH("src/assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(str(icon_path)))

    window = FunkerOptimizerREBORN()
    window.show()
    intro_screen.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()