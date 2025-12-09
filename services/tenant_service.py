# services/tenant_service.py
from database.db import get_db


def get_all_tenants():
    conn = get_db()
    return conn.execute(
        """
        SELECT tenant_id, full_name, sex, phone, id_number,
               address, birth, note
        FROM tenant
        WHERE is_deleted = 0
        ORDER BY tenant_id DESC
    """
    ).fetchall()


def get_tenant_count():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM tenant WHERE is_deleted = 0").fetchone()
    return row[0] if row else 0


def create_tenant(data: dict):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO tenant (full_name, sex, phone, id_number, address, birth, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data["full_name"],
            data["sex"],
            data["phone"],
            data["id_number"],
            data["address"],
            data["birth"],
            data["note"],
        ),
    )
    conn.commit()


def update_tenant(tenant_id: int, data: dict):
    conn = get_db()
    conn.execute(
        """
        UPDATE tenant SET full_name=?, sex=?, phone=?, id_number=?,
                          address=?, birth=?, note=?
        WHERE tenant_id = ?
    """,
        (
            data["full_name"],
            data["sex"],
            data["phone"],
            data["id_number"],
            data["address"],
            data["birth"],
            data["note"],
            tenant_id,
        ),
    )
    conn.commit()


def delete_tenant(tenant_id: int):
    conn = get_db()
    active = conn.execute(
        """
        SELECT 1 FROM contract WHERE tenant_id = ? AND contract_status = 'active' AND is_deleted = 0
    """,
        (tenant_id,),
    ).fetchone()
    if active:
        raise ValueError("Không thể xóa khách đang có hợp đồng hiệu lực!")
    conn.execute("UPDATE tenant SET is_deleted = 1 WHERE tenant_id = ?", (tenant_id,))
    conn.commit()

def get_tenant_by_id(tenant_id: int):
    conn = get_db()
    return conn.execute(
        "SELECT * FROM tenant WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()
