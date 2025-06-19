import tkinter as tk
from tkinter import messagebox
import win32api
import win32con

class ModeSwitcherApp:
    def __init__(self, master):
        self.master = master
        master.title("Mode Switcher")
        master.overrideredirect(True) # Hide the default system title bar

        # Set window size
        self.window_width = 220
        self.window_height = 120 # Updated from 100 to 120 for more space
        master.geometry(f"{self.window_width}x{self.window_height}")

        # Calculate bottom right corner position
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        pos_x = screen_width - self.window_width
        pos_y = screen_height - self.window_height

        master.geometry(f"+{pos_x - 20}+{pos_y - 90}")

        # --- Create custom title bar ---
        self.title_bar = tk.Frame(master, bg="#333333", relief="raised", bd=0) # Dark gray color
        self.title_bar.pack(expand=True, fill="x")

        # Close button
        self.close_button = tk.Button(self.title_bar, text="✕", command=self.close_window,
                                       font=("Arial", 10, "bold"), fg="white", bg="#333333",
                                       activebackground="red", activeforeground="white",
                                       relief="flat", bd=0, padx=5, pady=0)
        self.close_button.pack(side="right", padx=2)

        # Title text
        self.title_label = tk.Label(self.title_bar, text="Mode Switcher",
                                     font=("Arial", 10, "bold"), fg="white", bg="#333333")
        self.title_label.pack(side="left", padx=5)

        # Enable window dragging with custom title bar
        self.title_bar.bind("<Button-1>", self.start_move_window)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_label.bind("<Button-1>", self.start_move_window)
        self.title_label.bind("<B1-Motion>", self.move_window)

        # --- Apply styling to window content ---
        master.configure(bg="#000000") # Black background for content

        self.current_mode = tk.StringVar()
        self.current_mode.set("VIDEO") # Default mode

        # Frame containing buttons
        self.button_frame = tk.Frame(master, bg="#000000")
        self.button_frame.pack(pady=5)

        # --- Slide Mode Button ---
        self.slide_button = tk.Button(
            self.button_frame,
            text="Slide Mode",
            command=self.set_slide_mode,
            width=12, height=2,
            bg="#000000",          # Black background
            fg="white",            # White text
            relief="solid",        # Solid border
            borderwidth=1,         # Border thickness 1px
            highlightbackground="white", # Border color when not focused
            highlightcolor="white"       # Border color when focused
        )
        self.slide_button.pack(side=tk.LEFT, padx=5)
        # BIND NEW HOVER EFFECT
        self.slide_button.bind("<Enter>", lambda e: self.on_button_hover(self.slide_button, True))
        self.slide_button.bind("<Leave>", lambda e: self.on_button_hover(self.slide_button, False))

        # --- Video Mode Button ---
        self.video_button = tk.Button(
            self.button_frame,
            text="Video Mode",
            command=self.set_video_mode,
            width=12, height=2,
            bg="#000000",          # Black background
            fg="white",            # White text
            relief="solid",
            borderwidth=2,
            highlightbackground="white",
            highlightcolor="white"
        )
        self.video_button.pack(side=tk.RIGHT, padx=5)
        # BIND NEW HOVER EFFECT
        self.video_button.bind("<Enter>", lambda e: self.on_button_hover(self.video_button, True))
        self.video_button.bind("<Leave>", lambda e: self.on_button_hover(self.video_button, False))

        # Status label
        self.status_label = tk.Label(
            master,
            textvariable=self.current_mode,
            font=("Arial", 16, "bold"),
            fg="white", bg="#000000"
        )
        self.status_label.pack(pady=10)

    # --- Window move event handlers ---
    def start_move_window(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    # --- Close window ---
    def close_window(self):
        self.master.quit() # End Tkinter main loop

    # --- UPDATED HOVER EFFECT HANDLER ---
    def on_button_hover(self, button, is_hovering):
        hover_color = "#4F4FEB" # Blue color on hover
        default_color = "#000000" # Default black

        if is_hovering:
            # On hover: blue text and border, background unchanged
            button.config(fg=hover_color, highlightbackground=hover_color, highlightcolor=hover_color)
        else:
            # On leave: white text and border, background unchanged
            button.config(fg="white", highlightbackground="white", highlightcolor="white")

    def set_slide_mode(self):
        """Switch to Slide mode."""
        self.current_mode.set("SLIDE")
        print("Slide mode activated!")
        messagebox.showinfo("Mode", "Switched to SLIDE mode!")

    def set_video_mode(self):
        """Switch to Video mode."""
        self.current_mode.set("VIDEO")
        print("Video mode activated!")
        messagebox.showinfo("Mode", "Switched to VIDEO mode!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModeSwitcherApp(root)
    root.mainloop()