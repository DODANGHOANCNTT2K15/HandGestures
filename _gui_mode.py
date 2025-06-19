import tkinter as tk
from tkinter import messagebox
import win32api
import win32con
import json
import os
import threading

# Thư viện mới để tạo icon khay hệ thống
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageTk # Thư viện Pillow để xử lý hình ảnh

# Đường dẫn tới file chứa trạng thái mode
MODE_CONFIG_FILE = 'mode_config.json'
# Đường dẫn tới file icon cho khay hệ thống (nếu có, nếu không sẽ dùng icon mặc định)
APP_ICON_PATH = 'mode_switcher_icon.png' # Bạn có thể đặt file ảnh PNG của mình ở đây

# --- Hàm đọc/ghi trạng thái mode vào file JSON ---
def read_current_mode_from_file():
    """Đọc mode hiện tại từ file mode_config.json.
    Nếu file không tồn tại hoặc lỗi, trả về "VIDEO" làm mặc định."""
    try:
        with open(MODE_CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
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
        master.overrideredirect(True) # Giữ nguyên: Ẩn thanh tiêu đề mặc định của hệ thống

        # Thiết lập kích thước cửa sổ
        self.window_width = 220
        self.window_height = 120
        master.geometry(f"{self.window_width}x{self.window_height}")

        # Tính toán vị trí góc dưới bên phải màn hình
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        pos_x = screen_width - self.window_width - 20
        pos_y = screen_height - self.window_height - 90

        master.geometry(f"+{pos_x}+{pos_y}")

        # --- Tạo thanh tiêu đề tùy chỉnh ---
        self.title_bar = tk.Frame(master, bg="#333333", relief="raised", bd=0)
        self.title_bar.pack(expand=True, fill="x")

        # Nút đóng
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.close_app, # Sẽ đóng cả GUI và icon khay
                                         font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                         activebackground="red", activeforeground="white",
                                         relief="flat", bd=0, padx=5, pady=0)
        self.close_button.pack(side="right", padx=2)

        # Nút thu nhỏ/ẩn
        self.minimize_button = tk.Button(self.title_bar, text="—", command=self.minimize_to_tray, # Đã thay đổi
                                          font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                          activebackground="#555555", activeforeground="white",
                                          relief="flat", bd=0, padx=5, pady=0)
        self.minimize_button.pack(side="right", padx=2)

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
        master.configure(bg="#000000")

        self.current_mode_display = tk.StringVar(value=read_current_mode_from_file())

        self.button_frame = tk.Frame(master, bg="#000000")
        self.button_frame.pack(pady=5)

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
        self.slide_button.bind("<Enter>", lambda e: self.on_button_hover(self.slide_button, True))
        self.slide_button.bind("<Leave>", lambda e: self.on_button_hover(self.slide_button, False))

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
        self.video_button.bind("<Enter>", lambda e: self.on_button_hover(self.video_button, True))
        self.video_button.bind("<Leave>", lambda e: self.on_button_hover(self.video_button, False))

        self.status_label = tk.Label(
            master,
            textvariable=self.current_mode_display,
            font=("Arial", 16, "bold"),
            fg="white", bg="#000000"
        )
        self.status_label.pack(pady=10)

        # --- Thiết lập icon khay hệ thống ---
        self.tray_icon = None
        self.create_tray_icon()
        # Ẩn cửa sổ ban đầu và chỉ hiển thị icon khay hệ thống
        self.master.withdraw()
        
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

    # --- Tạo và quản lý icon khay hệ thống ---
    def create_tray_icon(self):
        try:
            # Tải ảnh icon từ đường dẫn đã cho
            image = Image.open(APP_ICON_PATH)
        except FileNotFoundError:
            print(f"Không tìm thấy file icon '{APP_ICON_PATH}'. Sử dụng icon mặc định.")
            # Tạo một hình ảnh đơn giản nếu không tìm thấy file icon
            image = Image.new('RGB', (64, 64), color = '#4F4FEB') # Màu xanh lam
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            try:
                # Cố gắng dùng font mặc định của hệ thống
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                # Nếu không tìm thấy Arial, dùng font mặc định của Pillow
                font = ImageFont.load_default()
            
            # Tính toán vị trí để chữ nằm giữa
            text = "MS"
            bbox = draw.textbbox((0,0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (image.width - text_width) / 2
            y = (image.height - text_height) / 2 - 5 # Điều chỉnh một chút cho cân đối
            draw.text((x,y), text, font=font, fill=(255,255,255)) # "MS" màu trắng

        # Định nghĩa menu cho icon khay hệ thống
        menu = Menu(MenuItem('Hiện cửa sổ', self.show_window_from_tray),
                    MenuItem('Chế độ Video', lambda icon, item: self.set_video_mode()),
                    MenuItem('Chế độ Slide', lambda icon, item: self.set_slide_mode()),
                    MenuItem('Thoát', self.close_app_from_tray))

        self.tray_icon = Icon("Mode Switcher", image, "Mode Switcher", menu)
        # Chạy icon khay hệ thống trong một luồng riêng
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # --- Ẩn cửa sổ và chỉ hiển thị icon khay hệ thống ---
    def minimize_to_tray(self):
        print("Cửa sổ đã được ẩn vào khay hệ thống.")
        self.master.withdraw() # Ẩn cửa sổ

    # --- Hiện cửa sổ từ khay hệ thống ---
    def show_window_from_tray(self, icon, item):
        # Sau khi ẩn, cần gọi deiconify trước rồi mới lift và focus để hiện đúng cách
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()
        print("Đã hiện lại cửa sổ.")

    # --- Đóng toàn bộ ứng dụng từ nút đóng GUI hoặc từ khay hệ thống ---
    def close_app(self):
        print("Đang đóng ứng dụng Mode Switcher...")
        if self.tray_icon:
            self.tray_icon.stop() # Dừng icon khay hệ thống
        self.master.quit() # Dừng vòng lặp chính của Tkinter

    # --- Đóng toàn bộ ứng dụng từ khay hệ thống ---
    def close_app_from_tray(self, icon, item):
        # Gọi hàm đóng ứng dụng chính từ luồng của pystray
        self.master.after(0, self.close_app)

    # --- Xử lý hiệu ứng Hover ---
    def on_button_hover(self, button, is_hovering):
        hover_color = "#4F4FEB"
        if is_hovering:
            button.config(fg=hover_color, highlightbackground=hover_color, highlightcolor=hover_color)
        else:
            button.config(fg="white", highlightbackground="white", highlightcolor="white")

    def set_slide_mode(self):
        current_mode_value = "SLIDE"
        self.current_mode_display.set(current_mode_value)
        write_current_mode_to_file(current_mode_value)
        print("Slide mode activated and updated in config!")

    def set_video_mode(self):
        current_mode_value = "VIDEO"
        self.current_mode_display.set(current_mode_value)
        write_current_mode_to_file(current_mode_value)
        print("Video mode activated and updated in config!")

if __name__ == "__main__":
    initial_mode = read_current_mode_from_file()
    write_current_mode_to_file(initial_mode)

    root = tk.Tk()
    app = ModeSwitcherApp(root)
    root.mainloop()