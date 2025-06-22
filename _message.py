import tkinter as tk
import json
import os
import time

MESSAGE_FILE_PATH = 'message.json'
CHECK_INTERVAL_MS = 1000 

if not os.path.exists(MESSAGE_FILE_PATH):
    initial_data = {"message": "Welcome to the application"}
    with open(MESSAGE_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=4)
    print(f"Created file '{MESSAGE_FILE_PATH}' with default initial message.")

def get_message_from_file(file_path: str = MESSAGE_FILE_PATH) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("message", "Error: Message key not found")
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in '{file_path}'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def send_message_to_file(new_message: str, file_path: str = MESSAGE_FILE_PATH):
    # Read old data
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
    except Exception:
        data = {}
    # Update message, keep other fields
    data["message"] = new_message
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Message '{new_message}' has been written to '{file_path}'.")
    except IOError as e:
        print(f"I/O error when writing to file '{file_path}': {e}")

class MessageDisplayApp:
    def __init__(self, master):
        self.master = master
        master.title("System Notification")

        # Hide border, always on top, hide taskbar
        master.overrideredirect(True)
        master.wm_attributes("-topmost", True)
        master.wm_attributes("-toolwindow", True)

        # Set gray background
        gray_bg = "#333333"
        master.config(bg=gray_bg)

        # Fixed window width 300px, height 30px
        self.window_width = 300
        self.window_height = 30
        master.geometry(f"{self.window_width}x{self.window_height}+20+{master.winfo_screenheight()-self.window_height-20}")

        # Main label
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

        # Shadow label
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

        # When updating message, update both labels
        truncated = self._truncate_message(self._get_current_message())
        self.message_label.config(text=truncated)
        self.shadow_label.config(text=truncated)
        self.last_displayed_message = truncated

        self.check_for_updates()

    def _get_current_message(self):
        return get_message_from_file(MESSAGE_FILE_PATH)

    def _truncate_message(self, message):
        # If exceeds 260px (estimated ~43 chars with font 10px), truncate
        max_chars = 43
        if len(message) > max_chars:
            return message[:max_chars - 3] + "..."
        return message

    def _reposition_window(self):
        # Reposition window at bottom left corner
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
            return True  # If error, do not stop

    def check_for_updates(self):
        current_message = self._get_current_message()
        truncated = self._truncate_message(current_message)

        # Check status, if false then stop program
        if not self._get_current_status():
            print("Received stop command from message.json. Exiting program.")
            self.master.destroy()
            return

        if truncated != self.last_displayed_message:
            self.message_label.config(text=truncated)
            self.shadow_label.config(text=truncated)
            self.last_displayed_message = truncated
            self._reposition_window()
            print(f"Message updated to: '{truncated}'")

        self.master.after(CHECK_INTERVAL_MS, self.check_for_updates)

def control_message():
    root = tk.Tk()
    app = MessageDisplayApp(root)
    root.mainloop()
    print("Application closed.")