import sys
import os

APP_NAME = "Funker Optimizer REBORN"
DIVISION_NUMBER = 2
DEFAULT_ANTIALIASING = True

COLOR_PRIMARY = "#4FC3F7"
COLOR_SECONDARY = "#1A237E"
COLOR_DARK = "#0D112D"
COLOR_TEXT = "#E0E0E0"
COLOR_WHITE = "#FFFFFF"
COLOR_YELLOW = "#FFFF8D"
COLOR_ACCENT = "#64B5F6"
COLOR_BG_LIGHT = "#1A1A3E"
COLOR_BG_DARK = "#0A0A1A"


def RESOURCE_PATH(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
