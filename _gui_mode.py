import tkinter as tk
from tkinter import messagebox
import win32api
import win32con

class ModeSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Mode Switcher")
        master.overrideredirect(True) # Ẩn thanh tiêu đề mặc định của hệ thống

        # Đặt kích thước cửa sổ
        self.window_width = 220
        self.window_height = 120 # Đã cập nhật từ 100 lên 120 để có thêm không gian
        master.geometry(f"{self.window_width}x{self.window_height}")

        # Tính toán vị trí góc dưới bên phải
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        pos_x = screen_width - self.window_width
        pos_y = screen_height - self.window_height

        master.geometry(f"+{pos_x - 20}+{pos_y - 90}")

        # --- Tạo thanh tiêu đề tùy chỉnh (Custom Title Bar) ---
        self.title_bar = tk.Frame(master, bg="#333333", relief="raised", bd=0) # Màu xám đậm
        self.title_bar.pack(expand=True, fill="x")

        # Nút đóng (Close Button)
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.close_window,
                                       font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                       activebackground="red", activeforeground="white",
                                       relief="flat", bd=0, padx=5, pady=0)
        self.close_button.pack(side="right", padx=2)

        # Tiêu đề văn bản (Title Text)
        self.title_label = tk.Label(self.title_bar, text="Mode Switcher",
                                     font=("Arial", 10, "bold"), fg="white", bg="#333333")
        self.title_label.pack(side="left", padx=5)

        # Kích hoạt chức năng kéo cửa sổ bằng thanh tiêu đề tùy chỉnh
        self.title_bar.bind("<Button-1>", self.start_move_window)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<Button-1>", self.start_move_window)
        self.title_label.bind("<B1-Motion>", self.move_window)

        # --- Áp dụng styling cho nội dung cửa sổ ---
        master.configure(bg="#000000") # Màu nền đen cho phần nội dung

        self.current_mode = tk.StringVar()
        self.current_mode.set("VIDEO") # Chế độ mặc định ban đầu

        # Frame chứa các nút
        self.button_frame = tk.Frame(master, bg="#000000")
        self.button_frame.pack(pady=5)

        # --- Nút Slide Mode ---
        self.slide_button = tk.Button(
            self.button_frame,
            text="Slide Mode",
            command=self.set_slide_mode,
            width=12, height=2,
            bg="#000000",          # Nền đen
            fg="white",            # Chữ trắng
            relief="solid",        # Viền liền
            borderwidth=1,         # Độ dày viền 1px
            highlightbackground="white", # Màu viền khi không focus
            highlightcolor="white"       # Màu viền khi focus
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
            bg="#000000",          # Nền đen
            fg="white",            # Chữ trắng
            relief="solid",
            borderwidth=2,
            highlightbackground="white",
            highlightcolor="white"
        )
        self.video_button.pack(side=tk.RIGHT, padx=5)
        # BIND HIỆU ỨNG HOVER MỚI
        self.video_button.bind("<Enter>", lambda e: self.on_button_hover(self.video_button, True))
        self.video_button.bind("<Leave>", lambda e: self.on_button_hover(self.video_button, False))

        # Nhãn hiển thị trạng thái
        self.status_label = tk.Label(
            master,
            textvariable=self.current_mode,
            font=("Arial", 16, "bold"),
            fg="white", bg="#000000"
        )
        self.status_label.pack(pady=10)

    # --- Hàm xử lý sự kiện di chuyển cửa sổ ---
    def start_move_window(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    # --- Hàm đóng cửa sổ ---
    def close_window(self):
        self.master.quit() # Kết thúc vòng lặp chính của Tkinter

    # --- HÀM XỬ LÝ HIỆU ỨNG HOVER ĐÃ CẬP NHẬT ---
    def on_button_hover(self, button, is_hovering):
        hover_color = "#4F4FEB" # Màu xanh (Blue) khi hover
        default_color = "#000000" # Màu đen mặc định

        if is_hovering:
            # Khi di chuột vào: chữ và viền xanh, nền không đổi
            button.config(fg=hover_color, highlightbackground=hover_color, highlightcolor=hover_color)
        else:
            # Khi di chuột ra: chữ và viền trắng, nền không đổi
            button.config(fg="white", highlightbackground="white", highlightcolor="white")

    def set_slide_mode(self):
        """Chuyển sang chế độ Slide."""
        self.current_mode.set("SLIDE")
        print("Chế độ Slide đã được kích hoạt!")
        messagebox.showinfo("Chế độ", "Đã chuyển sang chế độ SLIDE!")

    def set_video_mode(self):
        """Chuyển sang chế độ Video."""
        self.current_mode.set("VIDEO")
        print("Chế độ Video đã được kích hoạt!")
        messagebox.showinfo("Chế độ", "Đã chuyển sang chế độ VIDEO!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModeSwitcherApp(root)
    root.mainloop()