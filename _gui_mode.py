import tkinter as tk
from tkinter import messagebox
import win32api
import win32con
import json # Import thư viện json để làm việc với file config

# Đường dẫn tới file chứa trạng thái mode
MODE_CONFIG_FILE = 'mode_config.json'

# --- Hàm đọc/ghi trạng thái mode vào file JSON ---
def read_current_mode_from_file():
    """Đọc mode hiện tại từ file mode_config.json.
    Nếu file không tồn tại hoặc lỗi, trả về "VIDEO" làm mặc định."""
    try:
        with open(MODE_CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
            # Đảm bảo giá trị là 'VIDEO' hoặc 'SLIDE' và viết hoa
            mode = str(config_data.get('current_mode', 'VIDEO')).upper()
            if mode not in ["VIDEO", "SLIDE"]:
                print(f"Warning: Invalid mode '{mode}' found in config. Defaulting to 'VIDEO'.")
                mode = "VIDEO"
            return mode
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: '{MODE_CONFIG_FILE}' not found or invalid. Initializing with default mode 'VIDEO'.")
        write_current_mode_to_file('VIDEO') # Tạo file với mode mặc định
        return 'VIDEO'

def write_current_mode_to_file(mode):
    """Ghi mode hiện tại vào file mode_config.json."""
    try:
        with open(MODE_CONFIG_FILE, 'w') as f:
            json.dump({'current_mode': mode.upper()}, f, indent=2)
    except IOError as e:
        print(f"Error writing to '{MODE_CONFIG_FILE}': {e}")

class ModeSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Mode Switcher")
        master.overrideredirect(True) # Ẩn thanh tiêu đề mặc định của hệ thống

        # Thiết lập kích thước cửa sổ
        self.window_width = 220
        self.window_height = 120
        master.geometry(f"{self.window_width}x{self.window_height}")

        # Tính toán vị trí góc dưới bên phải màn hình
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # Offset từ góc dưới bên phải (điều chỉnh nếu cần)
        pos_x = screen_width - self.window_width - 20
        pos_y = screen_height - self.window_height - 90

        master.geometry(f"+{pos_x}+{pos_y}")

        # --- Tạo thanh tiêu đề tùy chỉnh ---
        self.title_bar = tk.Frame(master, bg="#333333", relief="raised", bd=0) # Màu xám đậm
        self.title_bar.pack(expand=True, fill="x")

        # Nút đóng
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.close_window,
                                       font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                       activebackground="red", activeforeground="white",
                                       relief="flat", bd=0, padx=5, pady=0)
        self.close_button.pack(side="right", padx=2)

        # Tiêu đề văn bản
        self.title_label = tk.Label(self.title_bar, text="Mode Switcher",
                                     font=("Arial", 10, "bold"), fg="white", bg="#333333")
        self.title_label.pack(side="left", padx=5)

        # Cho phép kéo cửa sổ bằng thanh tiêu đề tùy chỉnh
        self.title_bar.bind("<Button-1>", self.start_move_window)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<Button-1>", self.start_move_window)
        self.title_label.bind("<B1-Motion>", self.move_window)

        # --- Áp dụng kiểu dáng cho nội dung cửa sổ ---
        master.configure(bg="#000000") # Nền đen cho nội dung

        # Khởi tạo mode từ file config
        self.current_mode_display = tk.StringVar(value=read_current_mode_from_file()) # Biến Tkinter để hiển thị

        # Khung chứa các nút
        self.button_frame = tk.Frame(master, bg="#000000")
        self.button_frame.pack(pady=5)

        # --- Nút Slide Mode ---
        self.slide_button = tk.Button(
            self.button_frame,
            text="Slide Mode",
            command=self.set_slide_mode,
            width=12, height=2,
            bg="#000000",
            fg="white",
            relief="solid",
            borderwidth=1,
            highlightbackground="white",
            highlightcolor="white"
        )
        self.slide_button.pack(side=tk.LEFT, padx=5)
        # BIND HIỆU ỨNG HOVER MỚI
        self.slide_button.bind("<Enter>", lambda e: self.on_button_hover(self.slide_button, True))
        self.slide_button.bind("<Leave>", lambda e: self.on_button_hover(self.slide_button, False))

        # --- Nút Video Mode ---
        self.video_button = tk.Button(
            self.button_frame,
            text="Video Mode",
            command=self.set_video_mode,
            width=12, height=2,
            bg="#000000",
            fg="white",
            relief="solid",
            borderwidth=2,
            highlightbackground="white",
            highlightcolor="white"
        )
        self.video_button.pack(side=tk.RIGHT, padx=5)
        # BIND HIỆU ỨNG HOVER MỚI
        self.video_button.bind("<Enter>", lambda e: self.on_button_hover(self.video_button, True))
        self.video_button.bind("<Leave>", lambda e: self.on_button_hover(self.video_button, False))

        # Nhãn trạng thái
        self.status_label = tk.Label(
            master,
            textvariable=self.current_mode_display, # Sử dụng biến Tkinter
            font=("Arial", 16, "bold"),
            fg="white", bg="#000000"
        )
        self.status_label.pack(pady=10)

    # --- Xử lý sự kiện di chuyển cửa sổ ---
    def start_move_window(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    # --- Đóng cửa sổ ---
    def close_window(self):
        self.master.quit() # Kết thúc vòng lặp chính của Tkinter

    # --- Xử lý hiệu ứng Hover ---
    def on_button_hover(self, button, is_hovering):
        hover_color = "#4F4FEB" # Màu xanh lam khi hover
        if is_hovering:
            button.config(fg=hover_color, highlightbackground=hover_color, highlightcolor=hover_color)
        else:
            button.config(fg="white", highlightbackground="white", highlightcolor="white")

    def set_slide_mode(self):
        """Chuyển sang chế độ Slide và cập nhật file config."""
        current_mode_value = "SLIDE"
        self.current_mode_display.set(current_mode_value) # Cập nhật hiển thị trên GUI
        write_current_mode_to_file(current_mode_value) # Ghi mode mới vào file config
        print("Slide mode activated and updated in config!")

    def set_video_mode(self):
        """Chuyển sang chế độ Video và cập nhật file config."""
        current_mode_value = "VIDEO"
        self.current_mode_display.set(current_mode_value) # Cập nhật hiển thị trên GUI
        write_current_mode_to_file(current_mode_value) # Ghi mode mới vào file config
        print("Video mode activated and updated in config!")

if __name__ == "__main__":
    # Đảm bảo file mode_config.json tồn tại với giá trị mặc định khi khởi chạy lần đầu
    # hoặc khi file bị xóa/hỏng.
    initial_mode = read_current_mode_from_file()
    write_current_mode_to_file(initial_mode) # Đảm bảo file được tạo/cập nhật nếu cần

    root = tk.Tk()
    app = ModeSwitcherApp(root)
    root.mainloop()