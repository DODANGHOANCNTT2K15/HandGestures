# main.py
import cv2
import tkinter as tk
from gui import GUI
from hand_tracker import HandTracker
from gesture_controller import GestureController
from input_handler import InputHandler
from audio import Audio
from config import *
import threading
from queue import Queue
import time
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self):
        self.root = tk.Tk()
        self.cap = None
        for i in range(3):
            self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                break
        if not self.cap or not self.cap.isOpened():
            print("Không thể mở webcam.")
            exit()

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.gui = GUI(self.root, "Webcam Trực Tiếp với Tracking Tay", self.quit)
        self.hand_tracker = HandTracker(MAX_HANDS, MIN_DETECTION_CONFIDENCE)
        self.gesture_controller = GestureController(GESTURE_TIMEOUT)
        self.input_handler = InputHandler()
        self.audio = Audio(BEEP_ON_FREQ, BEEP_OFF_FREQ, BEEP_DURATION)

        self.imgtk = None
        self.frame_queue = Queue(maxsize=1)
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_frames, daemon=True)
        self.processing_thread.start()

    def process_frames(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                results = self.hand_tracker.process_frame(frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.hand_tracker.draw_landmarks(frame, hand_landmarks)

                text_lines = self.gesture_controller.update_gestures(
                    results,
                    self.hand_tracker,
                    self.frame_height,
                    self.audio.play_toggle_sound,      # on_toggle (Space)
                    self.input_handler.press_space,    # on_space
                    self.input_handler.adjust_volume,  # on_volume_adjust
                    self.audio.play_toggle_sound       # on_volume_toggle
                )
                self.gui.add_text(frame, text_lines)

                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.01)

    def update(self):
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                self.imgtk = ImageTk.PhotoImage(image=img)
                self.gui.canvas.imgtk = self.imgtk
                self.gui.canvas.configure(image=self.imgtk)
        except Exception as e:
            print(f"Lỗi trong update: {e}")

        self.root.after(10, self.update)

    def quit(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.hand_tracker.close()
        self.root.quit()

    def run(self):
        self.gui.start_loop(self.update, WEBCAM_DELAY)

if __name__ == "__main__":
    app = WebcamApp()
    app.run()