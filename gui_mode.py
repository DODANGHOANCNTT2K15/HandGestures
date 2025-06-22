import tkinter as tk
from tkinter import messagebox
import win32api
import win32con
import json
import threading

# New library for creating system tray icon
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageTk

from message import send_message_to_file 

MODE_CONFIG_FILE = 'mode_config.json'
APP_ICON_PATH = 'five.png' 

# --- Functions to read/write mode state to JSON file ---
def read_current_mode_from_file():
    try:
        with open(MODE_CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
            mode = str(config_data.get('current_mode', 'VIDEO')).upper()
            if mode not in ["VIDEO", "SLIDE"]:
                mode = "VIDEO"
            return mode
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: '{MODE_CONFIG_FILE}' not found or invalid. Initializing with default mode 'VIDEO'.")
        write_current_mode_to_file('VIDEO') 
        return 'VIDEO'

def write_current_mode_to_file(mode):
    try:
        with open(MODE_CONFIG_FILE, 'w') as f:
            json.dump({'current_mode': mode.upper()}, f, indent=2)
    except IOError as e:
        print(f"Error writing to '{MODE_CONFIG_FILE}': {e}")

def set_status_false():
    try:
        with open('message.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
    data['status'] = "false"
    with open('message.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class ModeSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Mode Switcher")
        master.overrideredirect(True) # Keep: Hide the system's default title bar

        # Set window size
        self.window_width = 220
        self.window_height = 120
        master.geometry(f"{self.window_width}x{self.window_height}")

        # Calculate position at bottom right corner of the screen
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        pos_x = screen_width - self.window_width - 20
        pos_y = screen_height - self.window_height - 90

        master.geometry(f"+{pos_x}+{pos_y}")

        # --- Create custom title bar ---
        self.title_bar = tk.Frame(master, bg="#333333", relief="raised", bd=0)
        self.title_bar.pack(expand=True, fill="x")

        # Close button
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.close_app, # Will close both GUI and tray icon
                                         font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                         activebackground="red", activeforeground="white",
                                         relief="flat", bd=0, padx=5, pady=0)
        self.close_button.pack(side="right", padx=2)

        # Minimize/hide button
        self.minimize_button = tk.Button(self.title_bar, text="—", command=self.minimize_to_tray, # Changed
                                          font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                          activebackground="#555555", activeforeground="white",
                                          relief="flat", bd=0, padx=5, pady=0)
        self.minimize_button.pack(side="right", padx=2)

        # Title text
        self.title_label = tk.Label(self.title_bar, text="Mode Switcher",
                                         font=("Arial", 10, "bold"), fg="white", bg="#333333")
        self.title_label.pack(side="left", padx=5)

        # Allow window dragging by custom title bar
        self.title_bar.bind("<Button-1>", self.start_move_window)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<Button-1>", self.start_move_window)
        self.title_label.bind("<B1-Motion>", self.move_window)

        # --- Apply style to window content ---
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

        # --- Set up system tray icon ---
        self.tray_icon = None
        self.create_tray_icon()
        # Hide window initially and only show system tray icon
        self.master.withdraw()
        
    # --- Handle window move events ---
    def start_move_window(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    # --- Create and manage system tray icon ---
    def create_tray_icon(self):
        try:
            # Load icon image from given path
            image = Image.open(APP_ICON_PATH)
        except FileNotFoundError:
            print(f"Icon file '{APP_ICON_PATH}' not found. Using default icon.")
            # Create a simple image if icon file not found
            image = Image.new('RGB', (64, 64), color = '#4F4FEB') # Blue color
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            try:
                # Try to use system default font
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                # If Arial not found, use Pillow's default font
                font = ImageFont.load_default()
            
            # Calculate position to center the text
            text = "MS"
            bbox = draw.textbbox((0,0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (image.width - text_width) / 2
            y = (image.height - text_height) / 2 - 5 # Adjust a bit for balance
            draw.text((x,y), text, font=font, fill=(255,255,255)) # "MS" in white

        # Define menu for system tray icon
        menu = Menu(MenuItem('Show Window', self.show_window_from_tray),
                    MenuItem('Video Mode', lambda icon, item: self.set_video_mode()),
                    MenuItem('Slide Mode', lambda icon, item: self.set_slide_mode()),
                    MenuItem('Exit', self.close_app_from_tray))

        self.tray_icon = Icon("Mode Switcher", image, "Mode Switcher", menu)
        # Run system tray icon in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # --- Hide window and only show system tray icon ---
    def minimize_to_tray(self):
        send_message_to_file("Window minimized to system tray.")
        self.master.withdraw() # Hide window

    # --- Show window from system tray ---
    def show_window_from_tray(self, icon, item):
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()
        send_message_to_file("Window restored from system tray.")

    # --- Close the entire app from GUI close button or system tray ---
    def close_app(self):
        set_status_false()  # Thêm dòng này để cập nhật
        if self.tray_icon:
            self.tray_icon.stop() # Stop system tray icon
        self.master.quit() # Stop Tkinter main loop

    # --- Close the entire app from system tray ---
    def close_app_from_tray(self, icon, item):
        # Call main app close function from pystray thread
        self.master.after(0, self.close_app)

    # --- Handle Hover effect ---
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
        send_message_to_file("Slide mode activated.")

    def set_video_mode(self):
        current_mode_value = "VIDEO"
        self.current_mode_display.set(current_mode_value)
        write_current_mode_to_file(current_mode_value)
        send_message_to_file("Video mode activated.")

# if __name__ == "__main__":
#     initial_mode = read_current_mode_from_file()
#     write_current_mode_to_file(initial_mode)

#     root = tk.Tk()
#     app = ModeSwitcherApp(root)
#     root.mainloop()

def control_gui_mode():
    initial_mode = read_current_mode_from_file()
    write_current_mode_to_file(initial_mode)

    root = tk.Tk()
    app = ModeSwitcherApp(root)
    root.mainloop()

    print("Application closed.")
