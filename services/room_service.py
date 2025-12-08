# services/room_service.py
from database.db import get_db
from utils.formatter import format_currency

# Dịch trạng thái
STATUS_EN = {"Trống": "available", "Đang thuê": "occupied", "Bảo trì": "maintenance"}
STATUS_VN = {v: k for k, v in STATUS_EN.items()}


# Lấy danh sách tất cả phòng chưa xóa
def get_all_rooms():
    conn = get_db()
    return conn.execute(
        """
                        SELECT room_id,
                               name_room,
                               area_m2,
                               floor,
                               base_rent,
                               electric_unit_price,
                               water_unit_price,
                               status,
                               note
                        FROM room
                        WHERE is_deleted = 0
                        ORDER BY room_id
                        """
    ).fetchall()


# Thêm phòng mới
def create_room(data: dict):
    conn = get_db()
    conn.execute(
        """
                 INSERT INTO room (
                     name_room,
                     area_m2, floor, base_rent, electric_unit_price,
                     water_unit_price, status, note
                 )
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                 """,
        (
            data["name_room"],
            data["area_m2"],
            data["floor"],
            data["base_rent"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["status"],
            data["note"],
        ),
    )
    conn.commit()


# Cập nhật thông tin phòng
def update_room(room_id: int, data: dict):
    conn = get_db()
    conn.execute(
        """
                 UPDATE room
                 SET name_room = ?,
                     area_m2 = ?,
                     floor = ?,
                     base_rent = ?,
                     electric_unit_price = ?,
                     water_unit_price = ?,
                     status = ?,
                     note = ?
                 WHERE room_id = ?
                 """,
        (
            data["name_room"],
            data["area_m2"],
            data["floor"],
            data["base_rent"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["status"],
            data["note"],
            room_id,
        ),
    )
    conn.commit()


# Xóa phòng (không cho xóa nếu đang có hợp đồng active)
def delete_room(room_id: int):
    conn = get_db()
    active_contract = conn.execute(
        """
                                   SELECT 1 FROM contract
                                   WHERE room_id = ? AND contract_status = 'active' AND is_deleted = 0
                                   """,
        (room_id,),
    ).fetchone()

    if active_contract:
        raise ValueError("Không thể xóa phòng đang có hợp đồng hiệu lực!")

    conn.execute("UPDATE room SET is_deleted = 1 WHERE room_id = ?", (room_id,))
    conn.commit()


# Lấy chi tiết 1 phòng theo ID
def get_room_by_id(room_id: int):
    conn = get_db()
    return conn.execute("SELECT * FROM room WHERE room_id = ?", (room_id,)).fetchone()


# Lấy danh sách phòng trống
def get_available_rooms():
    conn = get_db()
    return conn.execute(
        "SELECT * FROM room WHERE status = 'available' AND is_deleted = 0"
    ).fetchall()
