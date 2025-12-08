# ui/tabs/report_tab.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from services.report_service import (
    get_room_report, get_tenant_report,
    get_contract_report, get_bill_report
)


class ReportTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self._create_header()
        self._create_charts()

    # Header tiêu đề báo cáo
    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 15), padx=40)

        ctk.CTkLabel(
            header,
            text="BÁO CÁO TỔNG QUAN",
            font=("Inter", 32, "bold"),
            text_color="#1e293b"
        ).pack()

        ctk.CTkLabel(
            header,
            text="Dữ liệu báo cáo thống kê",
            font=("Inter", 14),
            text_color="#64748b"
        ).pack(pady=(0, 20))

    # Tạo 4 biểu đồ báo cáo: Phòng - Hóa đơn - Khách thuê - Hợp đồng
    def _create_charts(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=35, pady=10)
        main.grid_rowconfigure((0, 1), weight=1)
        main.grid_columnconfigure((0, 1), weight=1)

        room = get_room_report()
        tenant = get_tenant_report()
        contract = get_contract_report()
        bill = get_bill_report()

        self._bar_room(main, 0, 0, room)
        self._bar_bill(main, 0, 1, bill)
        self._pie_tenant(main, 1, 0, tenant)
        self._vbar_contract(main, 1, 1, contract)

    # Biểu đồ cột: Tình trạng phòng (Đang thuê / Trống / Bảo trì)
    def _bar_room(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        labels = ["Đang thuê", "Trống", "Bảo trì"]
        values = [data['occupied'], data['available'], data['maintenance']]
        colors = ["#3b82f6", "#10b981", "#f59e0b"]

        bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor='black', linewidth=1.2)

        ax.set_title("PHÒNG TRỌ", fontsize=13, fontweight='bold', pad=12, color="#1e293b")
        ax.set_ylabel("Số lượng", fontsize=10)
        ax.grid(True, axis='y', linestyle='--', alpha=0.4)
        ax.set_ylim(0, max(values, default=1) * 1.3)

        for bar in bars:
            height = int(bar.get_height())
            ax.text(bar.get_x() + bar.get_width()/2, height + max(values, default=1)*0.02,
                    str(height), ha='center', va='bottom',
                    fontweight='bold', fontsize=15, color="#1e293b")

        self._embed(fig, frame)

    # Biểu đồ cột: Hóa đơn (Đã thu / Chưa thu)
    def _bar_bill(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        labels = ["Đã thanh toán", "Chưa thanh toán"]
        values = [data['paid'], data['unpaid']]
        colors = ["#16a34a", "#ef4444"]

        bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor='black', linewidth=1.2)

        ax.set_title("HÓA ĐƠN", fontsize=13, fontweight='bold', pad=12, color="#1e293b")
        ax.set_ylabel("Số lượng", fontsize=10)
        ax.grid(True, axis='y', linestyle='--', alpha=0.4)
        ax.set_ylim(0, max(values, default=1) * 1.3)

        for bar in bars:
            height = int(bar.get_height())
            ax.text(bar.get_x() + bar.get_width()/2, height + max(values, default=1)*0.02,
                    str(height), ha='center', va='bottom',
                    fontweight='bold', fontsize=15, color="#1e293b")

        self._embed(fig, frame)

    # Biểu đồ tròn: Khách thuê (Đang thuê + Mới tháng này)
    def _pie_tenant(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        values = [data['active'], data['new_this_month']]
        labels = ["Đang thuê", "Mới tháng này"]
        colors = ["#10b981", "#8b5cf6"]

        wedges, _, autotexts = ax.pie(values, autopct=lambda p: f"{int(p/100*sum(values))}" if p > 0 else "",
                                     colors=colors, startangle=90,
                                     wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                                     textprops={'fontsize': 10, 'weight': 'bold', 'color': 'white'})

        ax.set_title("KHÁCH THUÊ", fontsize=13, fontweight='bold', pad=12)
        ax.legend(wedges, [f"{l}: {v}" for l, v in zip(labels, values)],
                  loc="lower center", bbox_to_anchor=(0.5, -0.08), ncol=1, fontsize=9)

        self._embed(fig, frame)

    # Biểu đồ cột dọc: Hợp đồng (Mới / Sắp hết / Đã hết)
    def _vbar_contract(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        labels = ["Mới", "Sắp hết", "Đã hết"]
        values = [data['new_this_month'], data['soon_expire'], data['ended']]
        colors = ["#8b5cf6", "#f59e0b", "#94a3b8"]

        x = np.arange(len(labels))
        bars = ax.bar(x, values, color=colors, width=0.55, edgecolor='black', linewidth=1.2)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
        ax.set_title("HỢP ĐỒNG", fontsize=13, fontweight='bold', pad=12)
        ax.grid(True, axis='y', linestyle='--', alpha=0.4)
        ax.set_ylim(0, max(values, default=1) * 1.3)

        for bar in bars:
            h = int(bar.get_height())
            ax.text(bar.get_x() + bar.get_width()/2, h + max(values, default=1)*0.02,
                    str(h), ha='center', va='bottom', fontweight='bold', fontsize=15)

        self._embed(fig, frame)

    # Tạo frame trắng chứa biểu đồ
    def _chart_frame(self, parent, r, c):
        f = ctk.CTkFrame(parent, fg_color="white", corner_radius=16, border_width=2, border_color="#e2e8f0")
        f.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
        return f

    # Nhúng biểu đồ matplotlib vào frame
    def _embed(self, fig, frame):
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)
        canvas.draw()