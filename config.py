# config.py
import os

# -----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn
FONT_PATH = os.path.join(ROOT_DIR, "assets", "fonts", "Inter.ttf")
BACKGROUND_IMAGE = os.path.join(ROOT_DIR, "assets", "background.jpg")
LOGO_PNG = os.path.join(ROOT_DIR, "assets", "logo.png")
LOGO_ICO = os.path.join(ROOT_DIR, "assets", "logo.ico")

# Màu sắc
PRIMARY_COLOR       = "#2563eb"
SECONDARY_COLOR     = "#475569"
ACCENT_COLOR        = "#3b82f6"
SUCCESS_COLOR       = "#10b981"
ERROR_COLOR         = "#ef4444"
WARNING_COLOR       = "#f59e0b"
TEXT_COLOR          = "#1e293b"
TEXT_LIGHT          = "#64748b"
BG_COLOR            = "#f8fafc"
CARD_BG             = "#ffffff"
BORDER_COLOR        = "#e2e8f0"

# Font
FONT_FAMILY = "Inter"
FONT_SIZE_SMALL     = 10
FONT_SIZE_REGULAR   = 12
FONT_SIZE_MEDIUM    = 14
FONT_SIZE_LARGE     = 16
FONT_SIZE_TITLE     = 24
FONT_SIZE_HEADER    = 32

# Đường dẫn hệ thống
DB_PATH = os.path.join(ROOT_DIR, "database", "rental.db")
PDF_OUTPUT_DIR = os.path.join(ROOT_DIR, "pdfs")