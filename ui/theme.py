# ui/theme.py
import customtkinter as ctk
from tkinter import font as tkfont
import os
import sys
import ctypes
from config import FONT_PATH, FONT_FAMILY, PRIMARY_COLOR


# =====================================#
# =====================================#
# =====================================#
def register_font():

    if not os.path.exists(FONT_PATH):
        print(f"Warning: Font not found: {FONT_PATH}")
        return False

    if sys.platform.startswith("win"):
        try:
            result = ctypes.windll.gdi32.AddFontResourceW(FONT_PATH)
            if result > 0:
                ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)
                print(f"Font '{FONT_FAMILY}' đã được đăng ký thành công!")
                return True
            else:
                print("Failed to register font (AddFontResourceW returned 0)")
        except Exception as e:
            print(f"Error registering font: {e}")
    else:
        print("Non-Windows: Font registration skipped. Please install Inter manually.")
    return False


# =====================================#
# =====================================#
# =====================================#
def setup_theme(root=None):
    register_font()
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    if root:
        root.configure(fg_color="#f8fafc")
    return True
