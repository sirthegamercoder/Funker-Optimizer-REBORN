import sys
import os

APP_NAME = "Funker Optimizer REBORN"
DIVISION_NUMBER = 2
DEFAULT_ANTIALIASING = True

COLOR_PRIMARY = "#4FC3F7"
COLOR_SECONDARY = "#1A237E"
COLOR_DARK = "#0D112D"
COLOR_TEXT = "#B0BEC5"
COLOR_WHITE = "#FFFFFF"
COLOR_YELLOW = "#FFFF8D"


def RESOURCE_PATH(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
