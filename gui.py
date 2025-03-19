# gui.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2

class GUI:
    def __init__(self, window, title, on_quit):
        self.window = window
        self.window.title(title)
        self.canvas = tk.Label(window)
        self.canvas.pack()
        self.btn_quit = tk.Button(window, text="Thoát", command=on_quit)
        self.btn_quit.pack()

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.configure(image=imgtk)

    def add_text(self, frame, text_lines):
        for i, line in enumerate(text_lines):
            cv2.putText(frame, line, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    def start_loop(self, update_callback, delay):
        self.window.after(delay, update_callback)
        self.window.mainloop()