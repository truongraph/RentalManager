import os
import subprocess
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = 0
        self.start_app()

    def start_app(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
        print("\n🔄 Khởi động lại ứng dụng...")
        self.process = subprocess.Popen([sys.executable, "main.py"])
        self.last_restart = time.time()

    def on_modified(self, event):
        # Chỉ reload file .py trong thư mục hiện tại, tránh spam reload
        if event.src_path.endswith(".py") and not event.is_directory:
            if time.time() - self.last_restart > 1:  # Debounce 1 giây
                print(f"\n📝 Phát hiện thay đổi: {os.path.basename(event.src_path)}")
                self.start_app()

if __name__ == "__main__":
    path = "."  # Theo dõi thư mục hiện tại
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("🚀 Đang theo dõi thay đổi... Sửa file .py → tự động reload!")
    print("Nhấn Ctrl+C để dừng.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dừng theo dõi...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()