# Hand Gesture Control
Control video with hand gestures via computer cam

## 📖 Introduction
This project uses a webcam and the Mediapipe library to recognize hand gestures, allowing you to control media functions such as play/pause (Space) and volume control on your computer. The program is written in Python, featuring a simple graphical interface and audio feedback.

---

## ✨ Features
### Media Control (Play/Pause - Space)
- **Activation:** Show both hands open, palms facing the camera, and hold for 1 second to toggle Space mode.
- **Execution:** When Space mode is active, make a fist (palm facing the camera) to send a Space or "K" key press (depending on the application).
- **Supported Applications:** YouTube, VLC, TikTok, Windows Media Player.

### Volume Control
- **Activation:** Show one hand making an "OK" gesture (thumb and index finger touching, other three fingers spread), hold for 0.5 seconds to toggle Volume mode. Plays a beep sound when toggling.
- **Increase Volume:** In Volume mode, right hand open and left hand in a fist — increases volume by 5% every 0.5 seconds.
- **Decrease Volume:** Right hand in a fist and left hand open — decreases volume by 5% every 0.5 seconds.
- **Technology:** Uses `pycaw` for precise volume control via Windows API.

### GUI and Feedback
- Displays webcam feed with hand landmark points (via Mediapipe).
- Shows real-time status: "Space Mode", "Volume Mode", and gesture information (Open, Fist, OK).
- Plays beep sounds (1000Hz when enabled, 500Hz when disabled) for toggle confirmation.

---

## 🚀 Technologies Used
- **Python:** Main programming language.
- **Mediapipe:** Hand gesture detection and tracking.
- **OpenCV:** Webcam video processing.
- **Tkinter:** Graphical interface.
- **Pycaw & Comtypes:** System volume control.
- **Pyautogui & Pygetwindow:** Sending media control key presses.

---

## 📥 Installation
### Requirements:
- Python 3.12+
- Functional webcam.

### Install Dependencies:
```bash
pip install mediapipe opencv-python tkinter pycaw comtypes pyautogui pygetwindow
```

### Run the Program:
```bash
python main.py
```

---

## ⚙️ How to Use
1. Run `main.py` to start the webcam interface.
2. Show your hand(s) in front of the camera and use the following gestures:
   - **Both hands open (1 second):** Toggle Space mode (Play/Pause control).
   - **Fist when Space mode is active:** Play/Pause the media.
   - **OK gesture (0.5 seconds):** Toggle Volume mode.
   - **Right hand open, left hand fist:** Increase volume.
   - **Right hand fist, left hand open:** Decrease volume.
3. Observe the on-screen status and listen for beep sounds.

---

## 📋 Notes
- Ensure good lighting conditions for accurate gesture recognition.
- When Volume mode is enabled, Space mode is disabled to prevent conflicts.
- Volume changes by 5% every 0.5 seconds, without displaying a progress bar (handled via `pycaw`).

---

## 📞 Author
- **Name:** DO DANG HOAN
- **Contact:** dodanghoana12017@gmail.com
