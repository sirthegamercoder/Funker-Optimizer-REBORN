import sys
import os
from pathlib import Path

APP_NAME = "Funker Optimizer REBORN"
DIVISION_NUMBER = 2
DEFAULT_ANTIALIASING = True

COLOR_PRIMARY = "#4FC3F7"
COLOR_SECONDARY = "#1A237E"
COLOR_DARK = "#0D112D"
COLOR_TEXT = "#B0BEC5"
COLOR_WHITE = "#FFFFFF"
COLOR_YELLOW = "#FFFF8D"


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent


def RESOURCE_PATH(relative_path):
    base_dir = get_base_dir()
    return str(base_dir / relative_path)


def CHOOSE_RESOURCE_PATH(relative_path):
    try:
        return RESOURCE_PATH(relative_path)
    except Exception:
        return FALLBACK_RESOURCE_PATH(relative_path)


def FALLBACK_RESOURCE_PATH(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
