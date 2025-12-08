# ui/tabs/home_tab.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from services.report_service import (
    get_room_report, get_tenant_report, get_contract_report,
    get_bill_report, get_revenue_last_6_months
)


class HomeTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")

        self._create_header()
        self._create_stats()
        self._create_charts()

    # Header chào mừng
    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(30, 15), padx=40)

        ctk.CTkLabel(header, text="Chào mừng quay trở lại!", font=("Inter", 34, "bold"), text_color="#1e293b").pack()
        ctk.CTkLabel(header, text="Thống kê tổng quan hệ thống", font=("Inter", 15), text_color="#64748b").pack(pady=(5, 30))

    # 6 ô thống kê nhanh (phòng, khách, hợp đồng, hóa đơn...)
    def _create_stats(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=(0, 25))
        frame.grid_columnconfigure((0,1,2), weight=1)

        room = get_room_report()
        tenant = get_tenant_report()
        contract = get_contract_report()
        bill = get_bill_report()

        stats = [
            ("Tổng phòng đang có", room['total'], "#3b82f6"),
            ("Đang được thuê", room['occupied'], "#10b981"),
            ("Tổng khách hàng", tenant['active'], "#8b5cf6"),
            ("Hợp đồng đang thuê", contract['new_this_month'] + contract['soon_expire'], "#f59e0b"),
            ("Hợp đồng sắp hết hạn", contract['soon_expire'], "#ef4444"),
            ("Hóa đơn chưa thu", bill['unpaid'], "#dc2626"),
        ]

        for i in range(2):
            for j in range(3):
                idx = i*3 + j
                if idx < len(stats):
                    t, v, c = stats[idx]
                    self._stat_card(frame, t, v, c, i, j)

    # Tạo 1 card thống kê nhỏ
    def _stat_card(self, parent, title, value, color, row, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=16, border_width=3, border_color=color)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(card, text=title, font=("Inter", 14), text_color="#475569").pack(pady=(18, 5))
        ctk.CTkLabel(card, text=str(value), font=("Inter", 42, "bold"), text_color=color).pack(pady=(0, 20))

    # 2 biểu đồ: Tình trạng phòng + Doanh thu 6 tháng
    def _create_charts(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=40, pady=10)
        frame.grid_columnconfigure((0,1), weight=1)
        frame.grid_rowconfigure(0, weight=1)

        c1 = ctk.CTkFrame(frame, fg_color="white", corner_radius=16, border_width=2, border_color="#e2e8f0")
        c1.grid(row=0, column=0, padx=(0, 12), pady=15, sticky="nsew")
        self._room_chart(c1)

        c2 = ctk.CTkFrame(frame, fg_color="white", corner_radius=16, border_width=2, border_color="#e2e8f0")
        c2.grid(row=0, column=1, padx=(12, 0), pady=15, sticky="nsew")
        self._revenue_chart(c2)

    # Biểu đồ cột: Trống / Đang thuê / Bảo trì
    def _room_chart(self, parent):
        room = get_room_report()
        values = [room['available'], room['occupied'], room['maintenance']]
        total = sum(values)

        fig = Figure(figsize=(4.5, 3.6), dpi=100)
        ax = fig.add_subplot(111)

        if total == 0:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu phòng',
                    ha='center', va='center', fontsize=16, color='#94a3b8')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines[['top', 'bottom', 'left', 'right']].set_visible(False)
        else:
            labels = ['Trống', 'Đang thuê', 'Bảo trì']
            colors = ['#10b981', '#3b82f6', '#f59e0b']

            bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor='black', linewidth=1.2)

            ax.set_title("Tình trạng phòng trọ", fontsize=13, fontweight='bold', pad=12, color="#1e293b")
            ax.set_ylabel("Số lượng", fontsize=10)
            ax.grid(True, axis='y', linestyle='--', alpha=0.4)

            # Tránh lỗi ylim khi tất cả bằng 0
            max_val = max(values) if max(values) > 0 else 1
            ax.set_ylim(0, max_val * 1.3)

            for bar in bars:
                h = int(bar.get_height())
                if h > 0:  # Chỉ hiện số khi > 0
                    ax.text(bar.get_x() + bar.get_width() / 2, h + max_val * 0.02,
                            str(h), ha='center', va='bottom', fontweight='bold', fontsize=14)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=14)
        canvas.draw()

    # Biểu đồ đường: Doanh thu 6 tháng gần nhất
    def _revenue_chart(self, parent):
        data = get_revenue_last_6_months()
        months = [d['month'] for d in data]
        revenues = [d['revenue'] for d in data]

        fig = Figure(figsize=(4.8, 3.6), dpi=100)
        ax = fig.add_subplot(111)

        # Kiểm tra nếu không có dữ liệu hoặc tất cả doanh thu = 0
        if not data or all(r == 0 for r in revenues):
            ax.text(0.5, 0.5, 'Chưa có dữ liệu doanh thu',
                    ha='center', va='center', fontsize=16, color='#94a3b8')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines[['top', 'bottom', 'left', 'right']].set_visible(False)
        else:
            ax.plot(months, revenues, 'o-', color='#10b981', linewidth=2.5, markersize=7,
                    markerfacecolor='white', markeredgewidth=2)
            ax.fill_between(months, revenues, alpha=0.15, color='#10b981')

            ax.set_title("Doanh thu 6 tháng (Đã thu)", fontsize=13, fontweight='bold', pad=12, color="#1e293b")
            ax.set_ylabel("VNĐ", fontsize=10)
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)

            max_rev = max(revenues) if max(revenues) > 0 else 1
            ax.set_ylim(0, max_rev * 1.3)

            for i, v in enumerate(revenues):
                if v > 0:
                    ax.text(i, v + max_rev * 0.05, f"{v:,}đ".replace(",", "."),
                            ha='center', va='bottom', fontweight='bold', fontsize=10)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=14)
        canvas.draw()