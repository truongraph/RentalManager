# services/contract_service.py
from database.db import get_db

# Lấy toàn bộ hợp đồng (kèm tên phòng + tên khách)
def get_all_contracts():
    conn = get_db()
    return conn.execute("""
        SELECT c.*, r.name_room, t.full_name
        FROM contract c
        JOIN room r ON c.room_id = r.room_id AND r.is_deleted = 0
        JOIN tenant t ON c.tenant_id = t.tenant_id AND t.is_deleted = 0
        WHERE c.is_deleted = 0
        ORDER BY c.contract_id DESC
    """).fetchall()

# Đếm số hợp đồng đang active
def get_active_contract_count():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM contract WHERE contract_status = 'active' AND is_deleted = 0").fetchone()
    return row[0] if row else 0

# Tạo hợp đồng mới + chuyển phòng sang occupied
def create_contract(data: dict):
    conn = get_db()
    conn.execute("""
        INSERT INTO contract (
            room_id, tenant_id, name_contact, start_ymd, end_ymd,
            rent, deposit_amount, electric_meter_start, water_meter_start,
            deposit_ymd, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['room_id'], data['tenant_id'], data['name_contact'],
        data['start_ymd'], data['end_ymd'], data['rent'],
        data['deposit_amount'], data['electric_meter_start'],
        data['water_meter_start'], data['deposit_ymd'], data['note']
    ))
    conn.execute("UPDATE room SET status = 'occupied' WHERE room_id = ?", (data['room_id'],))
    conn.commit()

# Cập nhật thông tin hợp đồng
def update_contract(contract_id: int, data: dict):
    conn = get_db()
    conn.execute("""
        UPDATE contract SET
            room_id = ?, tenant_id = ?, start_ymd = ?, end_ymd = ?,
            rent = ?, deposit_amount = ?, electric_meter_start = ?,
            water_meter_start = ?, deposit_ymd = ?, note = ?
        WHERE contract_id = ?
    """, (
        data['room_id'], data['tenant_id'],
        data['start_ymd'], data['end_ymd'],
        data['rent'], data['deposit_amount'],
        data['electric_meter_start'], data['water_meter_start'],
        data['deposit_ymd'], data['note'],
        contract_id
    ))
    conn.commit()

# Xóa hợp đồng + nếu đang active thì trả phòng về available
def delete_contract(contract_id: int):
    conn = get_db()
    room_id = conn.execute("SELECT room_id FROM contract WHERE contract_id = ?", (contract_id,)).fetchone()
    conn.execute("UPDATE contract SET is_deleted = 1 WHERE contract_id = ?", (contract_id,))
    if room_id:
        status = conn.execute("SELECT contract_status FROM contract WHERE contract_id = ?", (contract_id,)).fetchone()[0]
        if status == "active":
            conn.execute("UPDATE room SET status = 'available' WHERE room_id = ?", (room_id[0],))
    conn.commit()

# Kết thúc hợp đồng + trả phòng về available
def end_contract(contract_id: int):
    conn = get_db()
    room_id = conn.execute("SELECT room_id FROM contract WHERE contract_id = ?", (contract_id,)).fetchone()
    if room_id:
        conn.execute("UPDATE contract SET contract_status = 'ended' WHERE contract_id = ?", (contract_id,))
        conn.execute("UPDATE room SET status = 'available' WHERE room_id = ?", (room_id[0],))
    conn.commit()

# Lấy chi tiết 1 hợp đồng theo ID
def get_contract_by_id(contract_id: int):
    conn = get_db()
    return conn.execute("SELECT * FROM contract WHERE contract_id = ?", (contract_id,)).fetchone()

# Lấy danh sách phòng trống để lập hợp đồng
def get_available_rooms():
    conn = get_db()
    return conn.execute("""
        SELECT room_id, name_room, base_rent 
        FROM room 
        WHERE status = 'available' AND is_deleted = 0 
        ORDER BY room_id
    """).fetchall()

# Lấy khách chưa có hợp đồng active (dùng khi tạo hợp đồng mới)
def get_tenants_without_active_contract():
    conn = get_db()
    return conn.execute("""
        SELECT t.tenant_id, t.full_name 
        FROM tenant t
        LEFT JOIN contract c ON t.tenant_id = c.tenant_id 
            AND c.contract_status = 'active' AND c.is_deleted = 0
        WHERE c.contract_id IS NULL AND t.is_deleted = 0
        ORDER BY t.full_name
    """).fetchall()