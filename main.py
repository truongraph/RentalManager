# main.py
import sys
import signal
from ui.login import LoginPage
from ui.theme import register_font
#=====================================#
#=====================================#
#=====================================#
def signal_handler(sig, frame):
    print("\n\nĐã dừng chương trình. Tạm biệt nheeeeeeee hehe!")
    sys.exit(0)
#=====================================#
#=====================================#
#=====================================#
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        print(f"\nĐang khởi chạy app")
        register_font()
        app = LoginPage()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\nCó lỗi xảy ra: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("App đã đóng")