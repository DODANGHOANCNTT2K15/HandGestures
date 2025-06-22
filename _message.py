import tkinter as tk
import json
import os
import time

# --- Cấu hình ---
MESSAGE_FILE_PATH = 'message.json'
CHECK_INTERVAL_MS = 1000 # Kiểm tra mỗi 1 giây

# --- Đảm bảo file message.json tồn tại với nội dung ban đầu ---
if not os.path.exists(MESSAGE_FILE_PATH):
    initial_data = {"message": "Welcome to the application"}
    with open(MESSAGE_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=4)
    print(f"Đã tạo file '{MESSAGE_FILE_PATH}' với tin nhắn mặc định ban đầu.")

# --- Hàm đọc tin nhắn từ file ---
def get_message_from_file(file_path: str = MESSAGE_FILE_PATH) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("message", "Lỗi: Không tìm thấy khóa tin nhắn")
    except FileNotFoundError:
        return f"Lỗi: File '{file_path}' không tìm thấy."
    except json.JSONDecodeError:
        return f"Lỗi: JSON không hợp lệ trong '{file_path}'."
    except Exception as e:
        return f"Đã xảy ra lỗi không mong muốn: {e}"

# --- Hàm cập nhật tin nhắn vào file (cho mục đích thử nghiệm) ---
def send_message_to_file(new_message: str, file_path: str = MESSAGE_FILE_PATH):
    # Đọc dữ liệu cũ
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
    except Exception:
        data = {}
    # Cập nhật message, giữ nguyên các trường khác
    data["message"] = new_message
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Tin nhắn '{new_message}' đã được ghi vào '{file_path}'.")
    except IOError as e:
        print(f"Lỗi I/O khi ghi vào file '{file_path}': {e}")

# --- Thiết lập Tkinter cho cửa sổ hiển thị liên tục ---
class MessageDisplayApp:
    def __init__(self, master):
        self.master = master
        master.title("Thông Báo Hệ Thống")

        # Ẩn viền, luôn on top, ẩn taskbar
        master.overrideredirect(True)
        master.wm_attributes("-topmost", True)
        master.wm_attributes("-toolwindow", True)

        # Đặt màu nền xám
        gray_bg = "#333333"
        master.config(bg=gray_bg)

        # Cố định chiều rộng cửa sổ 300px, chiều cao 30px
        self.window_width = 300
        self.window_height = 30
        master.geometry(f"{self.window_width}x{self.window_height}+20+{master.winfo_screenheight()-self.window_height-20}")

        # Label chính
        self.message_label = tk.Label(
            master,
            text=self._get_current_message(),
            font=("Arial", 10, "bold"),
            bg=gray_bg, fg="white",
            padx=5, pady=2,
            anchor="w",
            justify="left"
        )
        self.message_label.pack(expand=True, fill="both")

        # Bóng chữ
        self.shadow_label = tk.Label(
            master,
            text=self._get_current_message(),
            font=("Arial", 10, "bold"),
            bg=gray_bg, fg="black",
            padx=5, pady=2,
            anchor="w",
            justify="left"
        )
        self.shadow_label.place(x=1, y=1, relwidth=1, relheight=1)
        self.message_label.lift()

        # Khi cập nhật message, cập nhật cả 2 label
        truncated = self._truncate_message(self._get_current_message())
        self.message_label.config(text=truncated)
        self.shadow_label.config(text=truncated)
        self.last_displayed_message = truncated

        self.check_for_updates()

    def _get_current_message(self):
        return get_message_from_file(MESSAGE_FILE_PATH)

    def _truncate_message(self, message):
        # Nếu vượt quá 260px (ước lượng ~43 ký tự với font 10px), thì cắt
        max_chars = 43
        if len(message) > max_chars:
            return message[:max_chars - 3] + "..."
        return message

    def _reposition_window(self):
        # Đặt lại vị trí cửa sổ ở góc trái dưới
        margin = 20
        x_pos = margin
        y_pos = self.master.winfo_screenheight() - self.window_height - margin 
        self.master.geometry(f"{self.window_width}x{self.window_height}+{x_pos}+{y_pos}")

    def _get_current_status(self):
        try:
            with open(MESSAGE_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return str(data.get("status", "true")).lower() == "true"
        except Exception:
            return True  # Nếu lỗi thì không dừng

    def check_for_updates(self):
        current_message = self._get_current_message()
        truncated = self._truncate_message(current_message)

        # Kiểm tra status, nếu là false thì dừng chương trình
        if not self._get_current_status():
            print("Đã nhận lệnh dừng từ message.json. Thoát chương trình.")
            self.master.destroy()
            return

        if truncated != self.last_displayed_message:
            self.message_label.config(text=truncated)
            self.shadow_label.config(text=truncated)
            self.last_displayed_message = truncated
            self._reposition_window()
            print(f"Tin nhắn đã cập nhật thành: '{truncated}'")

        self.master.after(CHECK_INTERVAL_MS, self.check_for_updates)

# --- Khối thực thi chính ---
if __name__ == "__main__":
    print("Bắt đầu ứng dụng hiển thị tin nhắn. Hãy chỉnh sửa file 'message.json' để thấy cập nhật.")
    print("Nhấn Ctrl+C trong console để dừng ứng dụng.")

    root = tk.Tk()
    app = MessageDisplayApp(root)
    root.mainloop() 

    print("Ứng dụng đã đóng.")