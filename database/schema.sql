-- database/schema.sql
PRAGMA foreign_keys = ON;

-- 1. Bảng user (quản trị viên)
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT,
    is_deleted INTEGER DEFAULT 0
);

-- 2. Bảng phòng trọ
CREATE TABLE IF NOT EXISTS room (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_room TEXT NOT NULL,                  -- Tên phòng
    area_m2 REAL,                             -- Diện tích (m²)
    floor INTEGER,                            -- Tầng
    base_rent REAL,                           -- Giá thuê cơ bản
    electric_unit_price REAL,                 -- Đơn giá điện
    water_unit_price REAL,                    -- Đơn giá nước
    status TEXT DEFAULT 'available',          -- available / occupied / maintenance
    note TEXT,
    is_deleted INTEGER DEFAULT 0
);

-- 3. Bảng khách thuê
CREATE TABLE IF NOT EXISTS tenant (
    tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    sex TEXT,                                 -- Nam / Nữ / Khác
    phone TEXT,
    id_number TEXT,                           -- CMND/CCCD
    address TEXT,
    birth DATE,
    note TEXT,
    is_deleted INTEGER DEFAULT 0
);

-- 4. Bảng hợp đồng thuê phòng
CREATE TABLE IF NOT EXISTS contract (
    contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER,
    tenant_id INTEGER,
    name_contact TEXT,                        -- Tên người đại diện hợp đồng
    start_ymd DATE,                           -- Ngày bắt đầu
    end_ymd DATE,                             -- Ngày kết thúc
    rent REAL,                                -- Tiền thuê thực tế (có thể khác base_rent)
    deposit_amount REAL,                      -- Tiền cọc
    electric_meter_start INTEGER,             -- Chỉ số điện ban đầu
    water_meter_start INTEGER,                -- Chỉ số nước ban đầu
    contract_status TEXT DEFAULT 'active',    -- active / ended
    deposit_ymd DATE,                         -- Ngày nộp cọc
    note TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES room(room_id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id) ON DELETE CASCADE
);

-- 5. Bảng hóa đơn tiền phòng - điện - nước
CREATE TABLE IF NOT EXISTS bill (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_code TEXT,                           -- Mã hóa đơn (tự sinh)
    contract_id INTEGER,
    bill_month TEXT,                          -- Format: 06/2025
    elec_prev INTEGER,                        -- Chỉ số điện kỳ trước
    elec_current INTEGER,                     -- Chỉ số điện kỳ này
    water_prev INTEGER,
    water_current INTEGER,
    electric_unit_price REAL,
    water_unit_price REAL,
    room_rent_amount REAL,                    -- Tiền phòng tháng này
    other_fee REAL DEFAULT 0,                 -- Phí khác
    total_amount REAL,                        -- Tổng phải trả
    paid_amount REAL DEFAULT 0,
    paid_status TEXT DEFAULT 'unpaid',        -- unpaid / paid
    paid_ymd DATE,                            -- Ngày thanh toán
    pdf_path TEXT,                            -- Đường dẫn file PDF hóa đơn
    note TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (contract_id) REFERENCES contract(contract_id) ON DELETE CASCADE
);

-- Tài khoản
INSERT INTO user (username, password, email)
VALUES ('admin', '123456', 'admin@gmail.com');