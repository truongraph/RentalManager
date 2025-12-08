# ui/login.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from services.login_service import authenticate_user
from ui.dashboard import Dashboard
from ui.theme import setup_theme
from config import LOGO_PNG


# =====================================#
# =====================================#
# =====================================#
class LoginPage(ctk.CTk):
    def __init__(self):

        super().__init__()
        setup_theme(self)

        self.title("Đăng nhập hệ thống - Hệ thống quản lý nhà trọ")
        self.geometry("480x680")
        self.resizable(False, False)
        self._center_window()

        try:
            self.iconbitmap("assets/logo.ico")
        except:
            pass

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 340
        self.geometry(f"480x680+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color="#E8F0FE")

        container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#ffffff",
        )
        container.pack(fill="both", expand=True, padx=40, pady=40)

        try:
            logo_img = Image.open(LOGO_PNG)
            logo = ctk.CTkImage(
                light_image=logo_img, dark_image=logo_img, size=(200, 40)
            )
            ctk.CTkLabel(container, image=logo, text="").pack(pady=(50, 10))
        except:
            ctk.CTkLabel(container, text="LOGO", font=("Inter", 50)).pack(pady=(50, 10))

        ctk.CTkLabel(
            container,
            text="Đăng nhập hệ thống",
            font=("Inter", 22, "bold"),
            text_color="#131313",
        ).pack(pady=(20, 0))
        ctk.CTkLabel(
            container,
            text="Nhập tên tài khoản và mật khẩu quản trị hệ thống",
            font=("Inter", 13),
            text_color="#888888",
        ).pack(pady=(0, 30))

        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(padx=50, fill="x")

        ctk.CTkLabel(form, text="Tên tài khoản", font=("Inter", 14, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        self.entry_user = ctk.CTkEntry(
            form,
            placeholder_text="Nhập tên tài khoản",
            height=50,
            corner_radius=10,
            font=("Inter", 16),
            fg_color="#f8fafc",
        )
        self.entry_user.pack(fill="x", pady=(0, 20))
        self.entry_user.focus()

        ctk.CTkLabel(form, text="Mật khẩu", font=("Inter", 14, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        self.entry_pass = ctk.CTkEntry(
            form,
            placeholder_text="Nhập mật khẩu",
            show="*",
            height=50,
            corner_radius=10,
            font=("Inter", 16),
            fg_color="#f8fafc",
        )
        self.entry_pass.pack(fill="x", pady=(0, 40))

        ctk.CTkButton(
            form,
            text="Đăng nhập ngay",
            command=self.login,
            height=50,
            corner_radius=10,
            font=("Inter", 16, "bold"),
            fg_color="#0042DC",
            hover_color="#013BC4",
        ).pack(fill="x")

        ctk.CTkLabel(
            container,
            text="Hệ thống quản lý nhà trọ © 2025 Nhóm 8",
            font=("Inter", 12),
            text_color="#000",
        ).pack(side="bottom", pady=30)

        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", lambda e: self.login())

    def login(self):

        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ!", parent=self)
            return

        result = authenticate_user(user, pwd)
        if result:
            self.withdraw()
            dash = Dashboard(user_id=1, login_window=self)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!", parent=self)
            self.entry_pass.delete(0, "end")
            self.entry_user.focus()
