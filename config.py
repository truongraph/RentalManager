# config.py
import os

# =====================================#
# =====================================#
# =====================================#
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# =====================================#
# =====================================#
# =====================================#
FONT_PATH = os.path.join(ROOT_DIR, "assets", "fonts", "Inter.ttf")
BACKGROUND_IMAGE = os.path.join(ROOT_DIR, "assets", "background.jpg")
LOGO_PNG = os.path.join(ROOT_DIR, "assets", "logo.png")
LOGO_ICO = os.path.join(ROOT_DIR, "assets", "logo.ico")
# =====================================#
# =====================================#
# =====================================#
PRIMARY_COLOR = "#225CD8"
SECONDARY_COLOR = "#475569"
ACCENT_COLOR = "#0067F7"
SUCCESS_COLOR = "#00B63E"
ERROR_COLOR = "#F50002"
WARNING_COLOR = "#f59e0b"
TEXT_COLOR = "#1e293b"
TEXT_LIGHT = "#1f1f1f"
BG_COLOR = "#f8fafc"
CARD_BG = "#ffffff"
BORDER_COLOR = "#e2e8f0"
# =====================================#
# =====================================#
# =====================================#
FONT_FAMILY = "Inter"
FONT_SIZE_SMALL = 10
FONT_SIZE_REGULAR = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_TITLE = 24
FONT_SIZE_HEADER = 32
# =====================================#
# =====================================#
# =====================================#
DB_PATH = os.path.join(ROOT_DIR, "database", "rental.db")
PDF_OUTPUT_DIR = os.path.join(ROOT_DIR, "pdfs")
