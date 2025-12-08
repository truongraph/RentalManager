# ui/tabs/tenant_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from services.tenant_service import get_all_tenants, create_tenant, update_tenant, delete_tenant


class TenantTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self.user_id = user_id
        self.current_tenant_id = None

        self._build_ui()
        self._load_data()

    # Xây dựng toàn bộ giao diện quản lý khách thuê
    def _build_ui(self):
        ctk.CTkLabel(self, text="QUẢN LÝ KHÁCH THUÊ", font=("Inter", 28, "bold"), text_color="#2756B5")\
            .pack(pady=(30, 20))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Hàng 1
        ctk.CTkLabel(form, text="Họ và tên *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w",
                                                                                pady=(0, 5))
        self.entry_name = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: Nguyễn Văn A")
        self.entry_name.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Số điện thoại", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w",
                                                                                  pady=(0, 5), padx=(30, 0))
        self.entry_phone = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                        placeholder_text="VD: 0901234567 (chỉ nhập 10 số)")
        self.entry_phone.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="CMND/CCCD", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w", pady=(0, 5),
                                                                              padx=(30, 0))
        self.entry_id = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                     placeholder_text="VD: 012345678901 (12 số)")
        self.entry_id.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Giới tính", font=("Inter", 14, "bold")).grid(row=0, column=3, sticky="w", pady=(0, 5),
                                                                              padx=(30, 0))
        self.combo_sex = ctk.CTkComboBox(form, values=["Nam", "Nữ", "Khác"],
                                         height=40, corner_radius=7, font=("Inter", 15), state="readonly")
        self.combo_sex.set("Nam")
        self.combo_sex.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))

        # Hàng 2
        ctk.CTkLabel(form, text="Ngày sinh", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(20, 5))
        self.cal_birth = DateEntry(form, height=40, corner_radius=7, date_pattern='dd/mm/yyyy', font=("Inter", 15),
                                   selectbackground="#3b82f6", selectforeground="white")
        self.cal_birth.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Địa chỉ thường trú", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w",
                                                                                       pady=(20, 5), padx=(30, 0))
        self.entry_address = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                          placeholder_text="VD: 123 Lê Lợi, Quận 1, TP. Hồ Chí Minh")
        self.entry_address.grid(row=3, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Ghi chú", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(20, 5),
                                                                            padx=(30, 0))
        self.entry_note = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: Sinh viên trường nào...")
        self.entry_note.grid(row=3, column=2, sticky="ew", columnspan=2, padx=(30, 0), pady=(0, 20))
        # Nút căn phải
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=(10, 30))
        btn_right = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_right.pack(side="right")

        self.btn_add = ctk.CTkButton(btn_right, text="Thêm Khách", height=44, corner_radius=7,
                                    font=("Inter", 15, "bold"), fg_color="#10b981", hover_color="#0d8b63",
                                    command=self.add_tenant)
        self.btn_add.pack(side="right", padx=8)

        self.btn_update = ctk.CTkButton(btn_right, text="Cập Nhật", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb",
                                       command=self.update_tenant)

        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa Khách", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#ef4444", hover_color="#dc2626",
                                       command=self.delete_tenant)

        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                      font=("Inter", 15, "bold"), fg_color="#64748b",
                                      command=self.reset_form)
        self.btn_reset.pack(side="right", padx=8)

        # Bảng danh sách khách thuê
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(0, 40))

        columns = ("id", "name", "sex", "phone", "id_number", "address", "birth", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headers = ["ID", "Họ tên", "Giới tính", "Điện thoại", "CMND/CCCD", "Địa chỉ", "Ngày sinh", "Ghi chú"]
        widths  = [80, 240, 110, 160, 180, 300, 140, 390]

        for col, text, w in zip(columns, headers, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col not in ["name", "address", "note"] else "w")

        style = ttk.Style()
        style.configure("Treeview", font=("Inter", 13), rowheight=52)
        style.configure("Treeview.Heading", font=("Inter", 14, "bold"))

        scroll = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scroll.pack(side="right", fill="y", padx=(0, 20), pady=20)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # Load toàn bộ khách thuê vào bảng
    def _load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for t in get_all_tenants():
            birth = ""
            if t["birth"]:
                try:
                    birth = datetime.strptime(t["birth"], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    birth = ""
            self.tree.insert("", "end", values=(
                t["tenant_id"],
                t["full_name"],
                t["sex"] or "—",
                t["phone"] or "—",
                t["id_number"] or "—",
                t["address"] or "—",
                birth or "—",
                t["note"] or ""
            ))

    # Reset form về trạng thái thêm mới
    def reset_form(self):
        self.current_tenant_id = None
        for e in (self.entry_name, self.entry_phone, self.entry_id, self.entry_address, self.entry_note):
            e.delete(0, "end")
        self.combo_sex.set("Nam")
        self.cal_birth.set_date(datetime.today())

        self.btn_add.pack(side="right", padx=8)
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()
        self.tree.selection_remove(self.tree.selection())

    # Click dòng → fill form + hiện nút sửa/xóa
    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.current_tenant_id = v[0]

        self.entry_name.delete(0, "end"); self.entry_name.insert(0, v[1])
        self.combo_sex.set(v[2] if v[2] != "—" else "Nam")
        self.entry_phone.delete(0, "end"); self.entry_phone.insert(0, v[3] if v[3] != "—" else "")
        self.entry_id.delete(0, "end"); self.entry_id.insert(0, v[4] if v[4] != "—" else "")
        self.entry_address.delete(0, "end"); self.entry_address.insert(0, v[5] if v[5] != "—" else "")
        self.entry_note.delete(0, "end"); self.entry_note.insert(0, v[7])

        if v[6] and v[6] != "—":
            try:
                d = datetime.strptime(v[6], "%d/%m/%Y")
                self.cal_birth.set_date(d)
            except:
                self.cal_birth.set_date(datetime.today())
        else:
            self.cal_birth.set_date(datetime.today())

        self.btn_add.pack_forget()
        self.btn_update.pack(side="right", padx=8)
        self.btn_delete.pack(side="right", padx=8)

    # Thêm khách thuê mới
    def add_tenant(self):
        if not self.entry_name.get().strip():
            messagebox.showwarning("Lỗi", "Nhập họ tên khách!")
            return

        birth = self.cal_birth.get_date().strftime("%Y-%m-%d")

        data = {
            "full_name": self.entry_name.get().strip(),
            "sex": self.combo_sex.get(),
            "phone": self.entry_phone.get().strip() or None,
            "id_number": self.entry_id.get().strip() or None,
            "address": self.entry_address.get().strip() or None,
            "birth": birth,
            "note": self.entry_note.get().strip() or None
        }
        create_tenant(data)
        messagebox.showinfo("Thành công", "Thêm khách thành công!")
        self._load_data()
        self.reset_form()

    # Cập nhật thông tin khách thuê
    def update_tenant(self):
        if not self.current_tenant_id: return

        birth = self.cal_birth.get_date().strftime("%Y-%m-%d")

        data = {
            "full_name": self.entry_name.get().strip(),
            "sex": self.combo_sex.get(),
            "phone": self.entry_phone.get().strip() or None,
            "id_number": self.entry_id.get().strip() or None,
            "address": self.entry_address.get().strip() or None,
            "birth": birth,
            "note": self.entry_note.get().strip() or None
        }
        update_tenant(self.current_tenant_id, data)
        messagebox.showinfo("Thành công", "Cập nhật thành công!")
        self._load_data()
        self.reset_form()

    # Xóa khách (không cho xóa nếu đang có hợp đồng active)
    def delete_tenant(self):
        if not self.current_tenant_id: return
        if messagebox.askyesno("Xác nhận", "Xóa khách thuê này?"):
            try:
                delete_tenant(self.current_tenant_id)
                messagebox.showinfo("Thành công", "Đã xóa khách!")
                self._load_data()
                self.reset_form()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))