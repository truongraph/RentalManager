# ui/dashboard.py
import customtkinter as ctk
from tkinter import messagebox
from ui.tabs.room_tab import RoomTab
from ui.tabs.tenant_tab import TenantTab
from ui.tabs.contract_tab import ContractTab
from ui.tabs.bill_tab import BillTab
from ui.tabs.home_tab import HomeTab
from ui.tabs.report_tab import ReportTab


class Dashboard(ctk.CTk):
    def __init__(self, user_id, login_window):
        super().__init__()
        self.user_id = user_id
        self.login_window = login_window

        self.title("Hệ thống quản lý nhà trọ")
        try:
            self.iconbitmap("assets/logo.ico")
        except:
            pass

        self.state('zoomed')
        self.configure(fg_color="#e8f5ff")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.active_button = None

        self._create_header()
        self._create_menu()
        self._create_responsive_content()
        self._create_footer()
        self._load_home()

        # Xác nhận thoát chương trình
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # Header
    def _create_header(self):
        header = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="#042549")
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="HỆ THỐNG QUẢN LÝ NHÀ TRỌ", font=("Inter", 32, "bold"), text_color="white")\
            .pack(side="left", padx=50, pady=20)

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=50, pady=25)

        ctk.CTkLabel(right, text="Chào mừng bạn, Admin", font=("Inter", 16, "bold"), text_color="white")\
            .pack(side="left", padx=(0,30))

        ctk.CTkButton(right, text="Đăng xuất", width=130, height=46, corner_radius=10,
                      font=("Inter", 14, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                      command=self._logout).pack(side="right")

    # Thanh menu ngang
    def _create_menu(self):
        menu = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#3279BB")
        menu.grid(row=1, column=0, sticky="ew")
        menu.pack_propagate(False)

        container = ctk.CTkFrame(menu, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        items = [
            ("Bảng điều khiển", self._load_home),
            ("Quản lý phòng", self._load_room),
            ("Quản lý khách", self._load_tenant),
            ("Quản lý hợp đồng", self._load_contract),
            ("Quản lý hóa đơn", self._load_bill),
            ("Báo cáo thống kê", self._load_report),
        ]

        for text, cmd in items:
            btn = ctk.CTkButton(container, text=text, width=180, height=40, corner_radius=7,
                                font=("Inter", 15, "bold"), fg_color="transparent",
                                hover_color="#F58220", text_color="white",
                                command=lambda c=cmd: self._set_active(c))
            btn.pack(side="left", padx=15)
            btn.cmd = cmd
            if text == "Bảng điều khiển":
                self.active_button = btn
                btn.configure(fg_color="#F58220")

    # Highlight nút đang được chọn
    def _set_active(self, cmd):
        if self.active_button:
            self.active_button.configure(fg_color="transparent")
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkFrame):
                for c in w.winfo_children():
                    if isinstance(c, ctk.CTkFrame):
                        for b in c.winfo_children():
                            if isinstance(b, ctk.CTkButton) and hasattr(b, 'cmd') and b.cmd == cmd:
                                self.active_button = b
                                b.configure(fg_color="#F58220")
                                break
        cmd()

    # Khu vực nội dung chính
    def _create_responsive_content(self):
        self.content = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=20,
                                              border_width=1, border_color="#e2e8f0")
        self.content.grid(row=2, column=0, sticky="nsew", padx=40, pady=30)

    # Footer
    def _create_footer(self):
        footer = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#f1f5f9")
        footer.grid(row=3, column=0, sticky="ew")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="© 2025 Nhóm 8 • Võ Đang Trường - Đỗ Ngọc Minh Tiến - Trần Ngọc Thái Bình - Lê Tấn Thành",
                     font=("Inter", 13, "bold"), text_color="#1e293b").pack(pady=22)

    # Xóa nội dung cũ trước khi load tab mới
    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # Load các tab
    def _load_home(self):     self._clear(); HomeTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)
    def _load_room(self):     self._clear(); RoomTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)
    def _load_tenant(self):   self._clear(); TenantTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)
    def _load_contract(self): self._clear(); ContractTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)
    def _load_bill(self):     self._clear(); BillTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)
    def _load_report(self):   self._clear(); ReportTab(self.content, self.user_id).pack(fill="both", expand=True, padx=30, pady=30)

    # Đăng xuất
    def _logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?", parent=self):
            self.destroy()
            self.login_window.deiconify()
            self.login_window.entry_user.delete(0, "end")
            self.login_window.entry_pass.delete(0, "end")
            self.login_window.entry_user.focus()

    # Xác nhận thoát toàn bộ chương trình
    def _on_close(self):
        if messagebox.askyesno("Thoát", "Thoát chương trình?", parent=self):
            self.login_window.destroy()
            self.destroy()