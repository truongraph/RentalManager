# ui/tabs/bill_tab.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import random
import string
from services.bill_service import (
    get_all_bills, create_bill, update_bill, delete_bill, mark_bill_paid,
    get_active_contracts_with_last_bill, get_next_bill_month, bill_exists
)
from utils.bill_pdf import generate_bill_pdf
from utils.formatter import format_currency, parse_currency


class BillTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self.user_id = user_id
        self.current_bill_id = None

        self._build_ui()
        self._load_data()
        self._refresh_contracts()

    # Tạo toàn bộ giao diện form + bảng danh sách
    def _build_ui(self):
        ctk.CTkLabel(self, text="QUẢN LÝ HÓA ĐƠN ĐIỆN NƯỚC", font=("Inter", 28, "bold"), text_color="#2756B5")\
            .pack(pady=(30, 20))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Hàng 1
        ctk.CTkLabel(form, text="Hợp đồng *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.combo_contract = ctk.CTkComboBox(form, values=[], state="readonly", height=40, corner_radius=7, font=("Inter", 15),
                                             command=lambda e: self._on_contract_selected())
        self.combo_contract.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Kỳ hóa đơn *", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(30, 0))
        self.entry_month = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15), placeholder_text="VD: 06/2025")
        self.entry_month.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Đồng hồ điện mới (kWh)", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w", pady=(0, 5), padx=(30, 0))
        self.entry_elec_new = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_elec_new.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_elec_new.bind("<KeyRelease>", lambda e: self._calculate_total())

        ctk.CTkLabel(form, text="Đồng hồ nước mới (m³)", font=("Inter", 14, "bold")).grid(row=0, column=3, sticky="w", pady=(0, 5), padx=(30, 0))
        self.entry_water_new = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_water_new.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_water_new.bind("<KeyRelease>", lambda e: self._calculate_total())

        # Hàng 2
        ctk.CTkLabel(form, text="Đồng hồ điện cũ", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(20, 5))
        self.lbl_elec_prev = ctk.CTkLabel(form, text="0", font=("Inter", 15, "bold"), text_color="#dc2626")
        self.lbl_elec_prev.grid(row=3, column=0, sticky="w")

        ctk.CTkLabel(form, text="Đồng hồ nước cũ", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w", pady=(20, 5), padx=(30, 0))
        self.lbl_water_prev = ctk.CTkLabel(form, text="0", font=("Inter", 15, "bold"), text_color="#dc2626")
        self.lbl_water_prev.grid(row=3, column=1, sticky="w", padx=(30, 0))

        ctk.CTkLabel(form, text="Tiền phòng", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(20, 5), padx=(30, 0))
        self.lbl_room_rent = ctk.CTkLabel(form, text="0 VNĐ", font=("Inter", 15, "bold"), text_color="#16a34a")
        self.lbl_room_rent.grid(row=3, column=2, sticky="w", padx=(30, 0))

        ctk.CTkLabel(form, text="Phí khác", font=("Inter", 14, "bold")).grid(row=2, column=3, sticky="w", pady=(20, 5), padx=(30, 0))
        self.entry_other_fee = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15), placeholder_text="0")
        self.entry_other_fee.grid(row=3, column=3, sticky="ew", padx=(30, 0))
        self.entry_other_fee.bind("<KeyRelease>", lambda e: self._calculate_total())

        # Tổng + Ghi chú
        total_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        total_frame.pack(pady=(10, 20), padx=60, anchor="e")
        ctk.CTkLabel(total_frame, text="TỔNG TIỀN:", font=("Inter", 18, "bold")).pack(side="left")
        self.lbl_total = ctk.CTkLabel(total_frame, text="0 VNĐ", font=("Inter", 26, "bold"), text_color="#dc2626")
        self.lbl_total.pack(side="left", padx=(10, 0))

        note_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        note_frame.pack(fill="x", padx=60, pady=(0, 20))
        ctk.CTkLabel(note_frame, text="Ghi chú:", font=("Inter", 14, "bold")).pack(side="left")
        self.entry_note = ctk.CTkEntry(note_frame, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_note.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Nút căn phải
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=(10, 30))
        btn_right = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_right.pack(side="right")

        self.btn_save = ctk.CTkButton(btn_right, text="Lập Hóa Đơn", height=44, corner_radius=7,
                                     font=("Inter", 15, "bold"), fg_color="#10b981", hover_color="#0d8b63",
                                     command=self._save_bill)
        self.btn_save.pack(side="right", padx=8)

        self.btn_update = ctk.CTkButton(btn_right, text="Cập Nhật", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb",
                                       command=self._update_bill)
        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                                       command=self._delete_bill)
        self.btn_print = ctk.CTkButton(btn_right, text="In Hóa Đơn", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#8b5cf6", hover_color="#7c3aed",
                                      command=self._print_bill)
        self.btn_paid = ctk.CTkButton(btn_right, text="Đã Thanh Toán", height=44, corner_radius=7,
                                     font=("Inter", 15, "bold"), fg_color="#16a34a", hover_color="#15803d",
                                     command=self._mark_paid)
        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#64748b",
                                      command=self._reset_form)
        self.btn_reset.pack(side="right", padx=8)

        # Bảng danh sách hóa đơn
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(0, 40))

        columns = ("id", "code", "room", "tenant", "month", "total", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headers = ["ID", "Mã HĐ", "Phòng", "Khách thuê", "Kỳ", "Tổng tiền", "Trạng thái"]
        widths  = [80, 120, 140, 250, 110, 180, 130]

        for col, text, w in zip(columns, headers, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col != "tenant" else "w")

        style = ttk.Style()
        style.configure("Treeview", font=("Inter", 13), rowheight=52)
        style.configure("Treeview.Heading", font=("Inter", 14, "bold"), background="#e2e8f0")

        scroll = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scroll.pack(side="right", fill="y", padx=(0, 20), pady=20)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # Load lại danh sách hợp đồng active vào combobox
    def _refresh_contracts(self):
        contracts = get_active_contracts_with_last_bill()
        values = [f"{c['contract_id']:02d} - {c['name_room']} - {c['full_name']}" for c in contracts]
        self.combo_contract.configure(values=values)
        if values:
            self.combo_contract.set(values[0])
            self._on_contract_selected()

    # Khi chọn hợp đồng → fill số cũ, tiền phòng, đề xuất kỳ tiếp theo
    def _on_contract_selected(self):
        if not self.combo_contract.get():
            return
        contract_id = int(self.combo_contract.get().split(" - ")[0])
        contract = next(c for c in get_active_contracts_with_last_bill() if c['contract_id'] == contract_id)

        self.lbl_elec_prev.configure(text=str(contract['elec_prev']))
        self.lbl_water_prev.configure(text=str(contract['water_prev']))
        self.lbl_room_rent.configure(text=f"{format_currency(contract['rent'])}")

        next_month = get_next_bill_month(contract_id)
        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, next_month)

        self._calculate_total()

    # Tính lại tổng tiền mỗi khi nhập số mới hoặc phí khác
    def _calculate_total(self):
        try:
            elec_new = int(self.entry_elec_new.get() or 0)
            water_new = int(self.entry_water_new.get() or 0)
            elec_prev = int(self.lbl_elec_prev.cget("text"))
            water_prev = int(self.lbl_water_prev.cget("text"))
            room_rent = parse_currency(self.lbl_room_rent.cget("text"))
            other_fee = parse_currency(self.entry_other_fee.get() or "0")

            contract_id = int(self.combo_contract.get().split(" - ")[0])
            contract = next(c for c in get_active_contracts_with_last_bill() if c['contract_id'] == contract_id)

            total = room_rent + \
                    (elec_new - elec_prev) * contract['electric_unit_price'] + \
                    (water_new - water_prev) * contract['water_unit_price'] + \
                    other_fee

            self.lbl_total.configure(text=f"{format_currency(int(total))} VNĐ")
        except:
            self.lbl_total.configure(text="0 VNĐ")

    # Lập hóa đơn mới
    def _save_bill(self):
        if not self.combo_contract.get() or not self.entry_month.get().strip():
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        contract_id = int(self.combo_contract.get().split(" - ")[0])
        bill_month = self.entry_month.get().strip()

        if bill_exists(contract_id, bill_month):
            messagebox.showerror("Lỗi", f"Hóa đơn kỳ {bill_month} đã tồn tại!")
            return

        contract = next(c for c in get_active_contracts_with_last_bill() if c['contract_id'] == contract_id)
        bill_code = "HD" + "".join(random.choices(string.digits, k=6))

        data = {
            "bill_code": bill_code,
            "contract_id": contract_id,
            "bill_month": bill_month,
            "elec_prev": int(self.lbl_elec_prev.cget("text")),
            "elec_current": int(self.entry_elec_new.get() or 0),
            "water_prev": int(self.lbl_water_prev.cget("text")),
            "water_current": int(self.entry_water_new.get() or 0),
            "electric_unit_price": contract['electric_unit_price'],
            "water_unit_price": contract['water_unit_price'],
            "room_rent_amount": contract['rent'],
            "other_fee": parse_currency(self.entry_other_fee.get() or "0"),
            "note": self.entry_note.get().strip()
        }

        create_bill(data)
        messagebox.showinfo("Thành công", f"Lập hóa đơn {bill_code} thành công!")
        self._load_data()
        self._reset_form()

    # Cập nhật hóa đơn đã chọn
    def _update_bill(self):
        if not self.current_bill_id:
            return
        # Code tương tự _save_bill nhưng dùng update_bill(self.current_bill_id, data)
        messagebox.showinfo("Info", "Chức năng cập nhật đang hoàn thiện bro!")

    # Xóa hóa đơn
    def _delete_bill(self):
        if messagebox.askyesno("Xác nhận", "Xóa hóa đơn này?"):
            delete_bill(self.current_bill_id)
            messagebox.showinfo("Thành công", "Đã xóa!")
            self._load_data()
            self._reset_form()

    # Xuất + mở file PDF hóa đơn
    def _print_bill(self):
        if not self.current_bill_id:
            return

        bill = next(b for b in get_all_bills() if b['bill_id'] == self.current_bill_id)
        bill_dict = dict(bill)
        try:
            path = generate_bill_pdf(bill_dict)
            messagebox.showinfo("Thành công", f"Đã xuất hóa đơn!\n{path}")
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể in:\n{e}")

    # Đánh dấu đã thanh toán
    def _mark_paid(self):
        mark_bill_paid(self.current_bill_id)
        messagebox.showinfo("Thành công", "Đã đánh dấu thanh toán!")
        self._load_data()

    # Khi click vào dòng trong bảng → fill form để sửa/in/xóa
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0])["values"]
        self.current_bill_id = values[0]

        bill = next(b for b in get_all_bills() if b['bill_id'] == self.current_bill_id)

        self.combo_contract.set(f"{bill['contract_id']:02d} - {bill['name_room']} - {bill['full_name']}")
        self.entry_month.delete(0, "end"); self.entry_month.insert(0, bill['bill_month'])
        self.entry_elec_new.delete(0, "end"); self.entry_elec_new.insert(0, str(bill['elec_current']))
        self.entry_water_new.delete(0, "end"); self.entry_water_new.insert(0, str(bill['water_current']))
        self.entry_other_fee.delete(0, "end"); self.entry_other_fee.insert(0, format_currency(bill['other_fee'] or 0))
        self.entry_note.delete(0, "end"); self.entry_note.insert(0, bill['note'] or "")

        self.lbl_elec_prev.configure(text=str(bill['elec_prev']))
        self.lbl_water_prev.configure(text=str(bill['water_prev']))
        self.lbl_room_rent.configure(text=f"{format_currency(bill['room_rent_amount'])}")
        self._calculate_total()

        # Hiển thị các nút phù hợp
        self.btn_save.pack_forget()
        self.btn_update.pack(side="right", padx=8)
        self.btn_delete.pack(side="right", padx=8)
        self.btn_print.pack(side="right", padx=8)
        if bill['paid_status'] == 'unpaid':
            self.btn_paid.pack(side="right", padx=8)
        else:
            self.btn_paid.pack_forget()

    # Load lại toàn bộ hóa đơn vào bảng
    def _load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for b in get_all_bills():
            status = "Đã thanh toán" if b['paid_status'] == 'paid' else "Chưa thanh toán"
            self.tree.insert("", "end", values=(
                b['bill_id'], b['bill_code'], b['name_room'], b['full_name'],
                b['bill_month'], format_currency(b['total_amount']), status
            ))

    # Reset form về trạng thái ban đầu (lập mới)
    def _reset_form(self):
        self.current_bill_id = None
        self.btn_save.pack(side="right", padx=8)
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()
        self.btn_print.pack_forget()
        self.btn_paid.pack_forget()

        self.entry_elec_new.delete(0, "end")
        self.entry_water_new.delete(0, "end")
        self.entry_other_fee.delete(0, "end"); self.entry_other_fee.insert(0, "0")
        self.entry_note.delete(0, "end")
        self.lbl_total.configure(text="0 VNĐ")
        self._refresh_contracts()