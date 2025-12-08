# utils/auth_state.py
import json
import os

STATE_FILE = "data/login_state.json"  # Đặt trong thư mục data để gọn

def save_login_state(user_id):
    """Lưu trạng thái đăng nhập"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    data = {"user_id": user_id, "remember": True}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_login_state():
    """Đọc trạng thái đăng nhập nếu có"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("remember"):
                return data.get("user_id")
    except:
        return None
    return None

def clear_login_state():
    """Xóa trạng thái khi đăng xuất"""
    if os.path.exists(STATE_FILE):
        try:
            os.remove(STATE_FILE)
        except:
            pass