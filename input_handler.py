# input_handler.py
import pyautogui
import pygetwindow as gw
import time

class InputHandler:
    def __init__(self):
        pass

    def press_space(self):
        active_window = gw.getActiveWindow()
        if not active_window:
            print("Không tìm thấy cửa sổ active!")
            return

        window_title = active_window.title.lower()

        if "youtube" in window_title:
            active_window.activate()
            time.sleep(0.1)
            pyautogui.press("k")
        elif "vlc" in window_title:
            active_window.activate()
            time.sleep(0.1)
            pyautogui.press("space")
        elif "tiktok" in window_title:
            active_window.activate()
            time.sleep(0.1)
            pyautogui.press("space")
        elif "media player" in window_title:
            active_window.activate()
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "p")
        else:
            active_window.activate()
            time.sleep(0.1)
            pyautogui.press("space")
            print(f"Không xác định được ứng dụng: {window_title}, gửi Space mặc định")

    def adjust_volume(self, direction):
        if direction == "increase":
            pyautogui.press("volumeup")
        elif direction == "decrease":
            pyautogui.press("volumedown")