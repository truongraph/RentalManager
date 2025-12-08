# ui/tabs/contract_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import os

from services.contract_service import (
    get_all_contracts, create_contract, update_contract,
    delete_contract, get_contract_by_id, end_contract,
    get_available_rooms, get_tenants_without_active_contract
)
from services.room_service import get_room_by_id
from services.tenant_service import get_tenant_by_id
from utils.contract_pdf import generate_contract_pdf
from utils.formatter import format_currency, parse_currency


class ContractTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self.user_id = user_id
        self.current_contract_id = None
        self.is_editing = False

        self._build_ui()
        self._load_data()
        self._refresh_comboboxes()

    # Xây dựng toàn bộ giao diện form + bảng danh sách hợp đồng
    def _build_ui(self):
        ctk.CTkLabel(self, text="QUẢN LÝ HỢP ĐỒNG THUÊ PHÒNG", font=("Inter", 28, "bold"), text_color="#2756B5")\
            .pack(pady=(30, 20))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # === HÀNG 1 ===
        ctk.CTkLabel(form, text="Phòng *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.combo_room = ctk.CTkComboBox(form, values=[], state="readonly", height=40, corner_radius=7,
                                         font=("Inter", 15), command=self._on_room_selected)
        self.combo_room.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Khách thuê *", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(30, 0))
        self.combo_tenant = ctk.CTkComboBox(form, values=[], state="readonly", height=40, corner_radius=7, font=("Inter", 15))
        self.combo_tenant.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Tiền thuê/tháng *", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w", pady=(0, 5), padx=(30, 0))
        self.entry_rent = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_rent.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_rent.bind("<KeyRelease>", lambda e: self._format_money(self.entry_rent))

        ctk.CTkLabel(form, text="Tiền cọc", font=("Inter", 14, "bold")).grid(row=0, column=3, sticky="w", pady=(0, 5), padx=(30, 0))
        self.entry_deposit = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_deposit.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_deposit.bind("<KeyRelease>", lambda e: self._format_money(self.entry_deposit))

        # === HÀNG 2 ===
        ctk.CTkLabel(form, text="Ngày nhận phòng *", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(15, 5))
        self.cal_start = DateEntry(form, date_pattern='dd/mm/yyyy', height=40, font=("Inter", 15), corner_radius=7)
        self.cal_start.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Ngày kết thúc", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w", pady=(15, 5), padx=(30, 0))
        self.cal_end = DateEntry(form, date_pattern='dd/mm/yyyy', height=40, font=("Inter", 15), corner_radius=7)
        self.cal_end.grid(row=3, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Ngày đặt cọc", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(15, 5), padx=(30, 0))
        self.cal_deposit = DateEntry(form, date_pattern='dd/mm/yyyy', height=40, font=("Inter", 15), corner_radius=7)
        self.cal_deposit.grid(row=3, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Đồng hồ điện (kWh)", font=("Inter", 14, "bold")).grid(row=2, column=3, sticky="w", pady=(15, 5), padx=(30, 0))
        self.entry_elec = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15), placeholder_text="VD: 1250")
        self.entry_elec.grid(row=3, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))

        # === HÀNG 3 ===
        ctk.CTkLabel(form, text="Đồng hồ nước (m³)", font=("Inter", 14, "bold")).grid(row=4, column=0, sticky="w", pady=(15, 5))
        self.entry_water = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15), placeholder_text="VD: 15")
        self.entry_water.grid(row=5, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Ghi chú", font=("Inter", 14, "bold")).grid(row=4, column=1, sticky="w", pady=(15, 5), padx=(30, 0), columnspan=3)
        self.entry_note = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_note.grid(row=5, column=1, sticky="ew", columnspan=3, padx=(30, 0), pady=(0, 20))

        # === NÚT CĂN PHẢI ===
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=(10, 30))
        btn_right = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_right.pack(side="right")

        self.btn_save = ctk.CTkButton(btn_right, text="Lập Hợp Đồng", height=44, corner_radius=7,
                                     font=("Inter", 15, "bold"), fg_color="#10b981", hover_color="#0d8b63",
                                     command=self._save_contract)
        self.btn_save.pack(side="right", padx=8)

        self.btn_update = ctk.CTkButton(btn_right, text="Cập Nhật", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb",
                                       command=self._update_contract)
        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa Hợp Đồng", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                                       command=self._delete_contract)
        self.btn_print = ctk.CTkButton(btn_right, text="In Hợp Đồng", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#8b5cf6", hover_color="#7c3aed",
                                      command=self._print_contract)
        self.btn_end = ctk.CTkButton(btn_right, text="Kết Thúc", height=44, corner_radius=7,
                                    font=("Inter", 15, "bold"), fg_color="#f59e0b", hover_color="#d97706",
                                    command=self._end_contract)
        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#64748b",
                                      command=self._reset_form)
        self.btn_reset.pack(side="right", padx=8)

        # === BẢNG DANH SÁCH HỢP ĐỒNG ===
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(0, 40))

        columns = ("id", "room", "tenant", "start", "rent", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headers = ["ID", "Phòng", "Khách thuê", "Nhận phòng", "Tiền thuê", "Trạng thái"]
        widths  = [80, 150, 320, 140, 180, 130]

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

    # Format tiền tự động khi nhập (thêm dấu chấm)
    def _format_money(self, widget):
        val = widget.get().replace(".", "").replace(" ", "")
        if val.isdigit():
            widget.delete(0, "end")
            widget.insert(0, format_currency(int(val)))

    # Load lại combobox phòng trống + khách chưa có hợp đồng
    def _refresh_comboboxes(self):
        rooms = get_available_rooms()
        tenants = get_tenants_without_active_contract()

        room_list = [f"{r['room_id']:02d} - {r['name_room']}" for r in rooms]
        tenant_list = [f"{t['tenant_id']:02d} - {t['full_name']}" for t in tenants]

        self.combo_room.configure(values=room_list)
        self.combo_tenant.configure(values=tenant_list)

        if not self.is_editing and len(room_list) == 1:
            self.combo_room.set(room_list[0])
            self._on_room_selected(room_list[0])

    # Khi chọn phòng → tự fill tiền thuê + đồng hồ = 0
    def _on_room_selected(self, value=None):
        if not self.combo_room.get(): return
        room_id = int(self.combo_room.get().split(" - ")[0])
        room = get_room_by_id(room_id)
        if room:
            self.entry_rent.delete(0, "end")
            self.entry_rent.insert(0, format_currency(room["base_rent"]))
            self.entry_elec.delete(0, "end"); self.entry_elec.insert(0, "0")
            self.entry_water.delete(0, "end"); self.entry_water.insert(0, "0")

    # Load toàn bộ hợp đồng vào bảng
    def _load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for c in get_all_contracts():
            status = "Đang thuê" if c["contract_status"] == "active" else "Đã kết thúc"
            start = datetime.strptime(c["start_ymd"], "%Y-%m-%d").strftime("%d/%m/%Y") if c["start_ymd"] else ""
            self.tree.insert("", "end", values=(
                c["contract_id"], c["name_room"], c["full_name"],
                start, format_currency(c["rent"]), status
            ))

    # Click vào dòng → fill form + hiện nút sửa/xóa/in/kết thúc
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.current_contract_id = v[0]
        self.is_editing = True

        contract = get_contract_by_id(self.current_contract_id)
        if not contract: return

        room_text = f"{contract['room_id']:02d} - {v[1]}"
        tenant_text = f"{contract['tenant_id']:02d} - {v[2]}"

        self.combo_room.set(room_text)
        self.combo_tenant.set(tenant_text)
        self.entry_rent.delete(0, "end")
        self.entry_rent.insert(0, format_currency(contract["rent"]))
        self.entry_deposit.delete(0, "end")
        self.entry_deposit.insert(0, format_currency(contract["deposit_amount"] or 0))
        self.entry_elec.delete(0, "end")
        self.entry_elec.insert(0, str(contract["electric_meter_start"] or 0))
        self.entry_water.delete(0, "end")
        self.entry_water.insert(0, str(contract["water_meter_start"] or 0))
        self.entry_note.delete(0, "end")
        self.entry_note.insert(0, contract["note"] or "")

        if contract["start_ymd"]:
            try: self.cal_start.set_date(datetime.strptime(contract["start_ymd"], "%Y-%m-%d"))
            except: pass
        if contract["end_ymd"]:
            try: self.cal_end.set_date(datetime.strptime(contract["end_ymd"], "%Y-%m-%d"))
            except: self.cal_end.set_date(None)
        else:
            self.cal_end.set_date(None)
        if contract["deposit_ymd"]:
            try: self.cal_deposit.set_date(datetime.strptime(contract["deposit_ymd"], "%Y-%m-%d"))
            except: pass

        self.btn_save.pack_forget()
        self.btn_update.pack(side="right", padx=8)
        self.btn_delete.pack(side="right", padx=8)
        self.btn_print.pack(side="right", padx=8)
        if contract["contract_status"] == "active":
            self.btn_end.pack(side="right", padx=8)
        else:
            self.btn_end.pack_forget()

    # Reset form về trạng thái lập hợp đồng mới
    def _reset_form(self):
        self.current_contract_id = None
        self.is_editing = False

        self.btn_save.pack(side="right", padx=8)
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()
        self.btn_print.pack_forget()
        self.btn_end.pack_forget()

        self.combo_room.set("")
        self.combo_tenant.set("")
        self.entry_rent.delete(0, "end")
        self.entry_deposit.delete(0, "end")
        self.entry_elec.delete(0, "end"); self.entry_elec.insert(0, "0")
        self.entry_water.delete(0, "end"); self.entry_water.insert(0, "0")
        self.entry_note.delete(0, "end")

        self.cal_start.set_date(datetime.today())
        self.cal_end.set_date(None)
        self.cal_deposit.set_date(datetime.today())

        self.tree.selection_remove(self.tree.selection())
        self._refresh_comboboxes()

    # Lập hợp đồng mới
    def _save_contract(self):
        if not self.combo_room.get() or not self.combo_tenant.get():
            messagebox.showwarning("Lỗi", "Vui lòng chọn phòng và khách thuê!")
            return

        room_id = int(self.combo_room.get().split(" - ")[0])
        tenant_id = int(self.combo_tenant.get().split(" - ")[0])

        data = {
            "room_id": room_id,
            "tenant_id": tenant_id,
            "name_contact": f"Hợp đồng phòng {self.combo_room.get().split(' - ')[1]}",
            "start_ymd": self.cal_start.get_date().strftime("%Y-%m-%d"),
            "end_ymd": self.cal_end.get_date().strftime("%Y-%m-%d") if self.cal_end.get_date() else None,
            "rent": parse_currency(self.entry_rent.get()),
            "deposit_amount": parse_currency(self.entry_deposit.get() or "0"),
            "electric_meter_start": int(self.entry_elec.get() or 0),
            "water_meter_start": int(self.entry_water.get() or 0),
            "deposit_ymd": self.cal_deposit.get_date().strftime("%Y-%m-%d"),
            "note": self.entry_note.get().strip() or None
        }
        create_contract(data)
        messagebox.showinfo("Thành công", "Lập hợp đồng thành công!")
        self._load_data()
        self._refresh_comboboxes()
        self._reset_form()

    # Cập nhật hợp đồng đang chọn
    def _update_contract(self):
        if not self.current_contract_id: return
        room_id = int(self.combo_room.get().split(" - ")[0])
        tenant_id = int(self.combo_tenant.get().split(" - ")[0])

        data = {
            "room_id": room_id, "tenant_id": tenant_id,
            "start_ymd": self.cal_start.get_date().strftime("%Y-%m-%d"),
            "end_ymd": self.cal_end.get_date().strftime("%Y-%m-%d") if self.cal_end.get_date() else None,
            "rent": parse_currency(self.entry_rent.get()),
            "deposit_amount": parse_currency(self.entry_deposit.get() or "0"),
            "electric_meter_start": int(self.entry_elec.get() or 0),
            "water_meter_start": int(self.entry_water.get() or 0),
            "deposit_ymd": self.cal_deposit.get_date().strftime("%Y-%m-%d"),
            "note": self.entry_note.get().strip() or None
        }
        update_contract(self.current_contract_id, data)
        messagebox.showinfo("Thành công", "Cập nhật hợp đồng thành công!")
        self._load_data()
        self._reset_form()

    # Xóa hợp đồng
    def _delete_contract(self):
        if messagebox.askyesno("Xác nhận", "Xóa hợp đồng này?\n(Dữ liệu sẽ bị ẩn, không thể khôi phục dễ dàng)"):
            delete_contract(self.current_contract_id)
            messagebox.showinfo("Thành công", "Đã xóa hợp đồng!")
            self._load_data()
            self._refresh_comboboxes()
            self._reset_form()

    # In hợp đồng ra PDF + mở file
    def _print_contract(self):
        if not self.current_contract_id: return
        contract = get_contract_by_id(self.current_contract_id)
        room = get_room_by_id(contract["room_id"])
        tenant = get_tenant_by_id(contract["tenant_id"])
        try:
            path = generate_contract_pdf(contract, room, tenant)
            messagebox.showinfo("Thành công", f"Đã xuất hợp đồng!\n{path}")
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể in hợp đồng:\n{e}")

    # Kết thúc hợp đồng + trả phòng về trống
    def _end_contract(self):
        if messagebox.askyesno("Xác nhận", "Kết thúc hợp đồng này?\nPhòng sẽ được trả về trạng thái Trống."):
            end_contract(self.current_contract_id)
            messagebox.showinfo("Thành công", "Đã kết thúc hợp đồng!")
            self._load_data()
            self._refresh_comboboxes()
            self._reset_form()