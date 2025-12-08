# ui/tabs/room_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.room_service import get_all_rooms, create_room, update_room, delete_room
from utils.formatter import format_currency, parse_currency


class RoomTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self.user_id = user_id
        self.current_room_id = None

        self._build_ui()
        self._load_data()

    # Xây dựng toàn bộ giao diện quản lý phòng
    def _build_ui(self):
        ctk.CTkLabel(self, text="QUẢN LÝ PHÒNG TRỌ", font=("Inter", 28, "bold"), text_color="#2756B5")\
            .pack(pady=(30, 20))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Hàng 1
        ctk.CTkLabel(form, text="Tên phòng *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w",
                                                                                pady=(0, 5))
        self.entry_name = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: Phòng 101")
        self.entry_name.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Số tầng (VD: 1)", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w",
                                                                                    pady=(0, 5), padx=(30, 0))
        self.entry_floor = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                        placeholder_text="VD: 1")
        self.entry_floor.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Diện tích (m²)", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w",
                                                                                   pady=(0, 5), padx=(30, 0))
        self.entry_area = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: 25")
        self.entry_area.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Giá thuê phòng (VNĐ/tháng)", font=("Inter", 14, "bold")).grid(row=0, column=3,
                                                                                               sticky="w", pady=(0, 5),
                                                                                               padx=(30, 0))
        self.entry_rent = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: 2.500.000")
        self.entry_rent.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_rent.bind("<KeyRelease>", self._format_money)

        # Hàng 2
        ctk.CTkLabel(form, text="Giá điện (VNĐ/kWh)", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w",
                                                                                       pady=(0, 5))
        self.entry_elec = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: 3.500")
        self.entry_elec.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.entry_elec.bind("<KeyRelease>", self._format_money)

        ctk.CTkLabel(form, text="Giá nước (VNĐ/m³)", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w",
                                                                                      pady=(0, 5), padx=(30, 0))
        self.entry_water = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                        placeholder_text="VD: 10.000")
        self.entry_water.grid(row=3, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_water.bind("<KeyRelease>", self._format_money)

        ctk.CTkLabel(form, text="Trạng thái", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(0, 5),
                                                                               padx=(30, 0))
        self.combo_status = ctk.CTkComboBox(form, values=["Trống", "Đang thuê", "Bảo trì"],
                                            height=40, corner_radius=7, font=("Inter", 15), state="readonly")
        self.combo_status.set("Trống")
        self.combo_status.grid(row=3, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Ghi chú", font=("Inter", 14, "bold")).grid(row=2, column=3, sticky="w", pady=(0, 5),
                                                                            padx=(30, 0))
        self.entry_note = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: Có gác lửng, toilet riêng...")
        self.entry_note.grid(row=3, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))

        # Nút căn phải
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=(10, 30))
        btn_right = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_right.pack(side="right")

        self.btn_add = ctk.CTkButton(btn_right, text="Thêm Phòng", height=44, corner_radius=7,
                                    font=("Inter", 15, "bold"), fg_color="#10b981", hover_color="#0d8b63",
                                    command=self.add_room)
        self.btn_add.pack(side="right", padx=8)

        self.btn_update = ctk.CTkButton(btn_right, text="Cập Nhật", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb",
                                       command=self.update_room)

        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa Phòng", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                                       command=self.delete_room)

        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#64748b",
                                      command=self.reset_form)
        self.btn_reset.pack(side="right", padx=8)

        # Bảng danh sách phòng
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(0, 40))

        columns = ("id", "name", "floor", "area", "rent", "elec", "water", "status", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headers = ["ID", "Tên phòng", "Tầng", "Diện tích", "Giá thuê/tháng", "Giá điện", "Giá nước", "Trạng thái", "Ghi chú"]
        widths  = [80, 240, 110, 140, 200, 170, 170, 150, 340]

        for col, text, w in zip(columns, headers, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col not in ["name", "note"] else "w")

        style = ttk.Style()
        style.configure("Treeview", font=("Inter", 13), rowheight=52)
        style.configure("Treeview.Heading", font=("Inter", 14, "bold"), background="#e2e8f0")

        scroll = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scroll.pack(side="right", fill="y", padx=(0, 20), pady=20)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # Format tiền tự động khi nhập
    def _format_money(self, event):
        w = event.widget
        val = w.get().replace(".", "")
        if val.isdigit():
            w.delete(0, "end")
            w.insert(0, format_currency(int(val)))

    # Load toàn bộ phòng vào bảng
    def _load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        status_vn = {"available": "Trống", "occupied": "Đang thuê", "maintenance": "Bảo trì"}
        for r in get_all_rooms():
            self.tree.insert("", "end", values=(
                r["room_id"],
                r["name_room"],
                r["floor"] or "-",
                r["area_m2"] or "-",
                format_currency(r["base_rent"]),
                format_currency(r["electric_unit_price"]),
                format_currency(r["water_unit_price"]),
                status_vn.get(r["status"], r["status"]),
                r["note"] or ""
            ))

    # Reset form về trạng thái thêm mới
    def reset_form(self):
        self.current_room_id = None
        for e in (self.entry_name, self.entry_area, self.entry_floor,
                  self.entry_rent, self.entry_elec, self.entry_water, self.entry_note):
            e.delete(0, "end")
        self.combo_status.set("Trống")

        self.btn_add.pack(side="right", padx=8)
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()
        self.tree.selection_remove(self.tree.selection())

    # Click vào dòng → fill form + hiện nút sửa/xóa
    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.current_room_id = v[0]

        self.entry_name.delete(0, "end"); self.entry_name.insert(0, v[1])
        self.entry_floor.delete(0, "end"); self.entry_floor.insert(0, str(v[2]) if v[2] != "-" else "")
        self.entry_area.delete(0, "end"); self.entry_area.insert(0, str(v[3]) if v[3] != "-" else "")
        self.entry_rent.delete(0, "end"); self.entry_rent.insert(0, v[4])
        self.entry_elec.delete(0, "end"); self.entry_elec.insert(0, v[5])
        self.entry_water.delete(0, "end"); self.entry_water.insert(0, v[6])
        self.combo_status.set(v[7])
        self.entry_note.delete(0, "end"); self.entry_note.insert(0, v[8])

        self.btn_add.pack_forget()
        self.btn_update.pack(side="right", padx=8)
        self.btn_delete.pack(side="right", padx=8)

    # Thêm phòng mới (kiểm tra trùng tên)
    def add_room(self):
        if not self.entry_name.get().strip():
            messagebox.showwarning("Lỗi", "Nhập tên phòng!")
            return
        name = self.entry_name.get().strip().upper()
        if any(r["name_room"].upper() == name for r in get_all_rooms()):
            messagebox.showwarning("Trùng", "Tên phòng đã tồn tại!")
            return

        data = {
            "name_room": name,
            "area_m2": float(self.entry_area.get() or 0),
            "floor": int(self.entry_floor.get() or 0) or None,
            "base_rent": parse_currency(self.entry_rent.get() or "0"),
            "electric_unit_price": parse_currency(self.entry_elec.get() or "3500"),
            "water_unit_price": parse_currency(self.entry_water.get() or "10000"),
            "status": {"Trống": "available", "Đang thuê": "occupied", "Bảo trì": "maintenance"}[self.combo_status.get()],
            "note": self.entry_note.get().strip() or None
        }
        create_room(data)
        messagebox.showinfo("Thành công", "Thêm phòng thành công!")
        self._load_data()
        self.reset_form()

    # Cập nhật thông tin phòng
    def update_room(self):
        if not self.current_room_id: return
        data = {
            "name_room": self.entry_name.get().strip(),
            "area_m2": float(self.entry_area.get() or 0),
            "floor": int(self.entry_floor.get() or 0) or None,
            "base_rent": parse_currency(self.entry_rent.get()),
            "electric_unit_price": parse_currency(self.entry_elec.get()),
            "water_unit_price": parse_currency(self.entry_water.get()),
            "status": {"Trống": "available", "Đang thuê": "occupied", "Bảo trì": "maintenance"}[self.combo_status.get()],
            "note": self.entry_note.get().strip() or None
        }
        update_room(self.current_room_id, data)
        messagebox.showinfo("Thành công", "Cập nhật thành công!")
        self._load_data()
        self.reset_form()

    # Xóa phòng (không cho xóa nếu đang có hợp đồng active)
    def delete_room(self):
        if not self.current_room_id: return
        if messagebox.askyesno("Xác nhận", "Xóa phòng này?"):
            try:
                delete_room(self.current_room_id)
                messagebox.showinfo("Thành công", "Đã xóa phòng!")
                self._load_data()
                self.reset_form()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))