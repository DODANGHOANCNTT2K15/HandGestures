import subprocess
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
import win32api
import win32con
import time
import os  
import joblib
import win32gui  
import json

MODEL_PATH = 'gesture_recognition_model.h5'
SCALER_PATH = 'scaler.pkl' 

# region load the trained model and scaler
if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    print(f"Error: Model file ('{MODEL_PATH}') or scaler ('{SCALER_PATH}') not found.")
    print("Please run 'train_model.py' first to train and save them.")
    exit()
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print(f"Successfully loaded model from '{MODEL_PATH}' and scaler from '{SCALER_PATH}'.")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    print("Please check file paths and formats.")
    exit()
# endregion

# Define gesture mappings
GESTURES = {}

def focus_powerpoint_slideshow():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "PowerPoint Slide Show" in title:
                result.append(hwnd)
    result = []
    win32gui.EnumWindows(enum_handler, result)
    if result:
        win32gui.SetForegroundWindow(result[0])
        return True
    return False

def get_gesture_mappings(class_name):
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
        mapping = config.get(class_name)
        if mapping is not None:
            # Convert key from str to int
            return {int(k): v for k, v in mapping.items()}
        return {}

def send_play_pause():
    """Simulate media play/pause key press"""
    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)

def predict_gesture(landmarks):
    """Convert landmarks to model input and predict gesture"""
    # Flatten landmarks to match training data format
    row = []
    for landmark in landmarks.landmark:
        row.extend([landmark.x, landmark.y, landmark.z])
    
    # Scale the features
    scaled_row = scaler.transform([row])
    
    # Predict
    prediction = model.predict(scaled_row)
    predicted_class = np.argmax(prediction[0])
    
    return predicted_class

def control_video():
    print(GESTURES)
    # region initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.9,
        min_tracking_confidence=0.9)
    mp_draw = mp.solutions.drawing_utils
    #endregion

    # region gui camera
    # Initialize camera
    cap = cv2.VideoCapture(0)

    # Create and position window without title bar and shadow
    window_name = 'Gesture Control'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    hwnd = win32gui.FindWindow(None, window_name)
    
    # Remove window border, title bar, and shadow
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style = style & ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | 
                     win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
    # Remove extended window styles (including shadow)
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style = ex_style & ~(win32con.WS_EX_DLGMODALFRAME | win32con.WS_EX_CLIENTEDGE | 
                           win32con.WS_EX_STATICEDGE | win32con.WS_EX_WINDOWEDGE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    
    # Get screen resolution
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # Set window size
    window_width = 320
    window_height = 240
    
    # Calculate position (e.g., top-right corner with 20px margin)
    pos_x = (screen_width - window_width) // 2
    pos_y = 20

    # Set window position and size
    win32gui.SetWindowPos(hwnd, 
                         win32con.HWND_TOPMOST,  # Changed to HWND_TOPMOST to keep window on top
                         pos_x, pos_y,
                         window_width, window_height,
                         win32con.SWP_SHOWWINDOW)
    #endregion

    # region Control variables
    window_visible = False
    gesture_key = list(GESTURES)
    # endregion

    # region test gesture
    queue_templates = {
        "queue1": [gesture_key[5], gesture_key[6]], 
        "queue2": [gesture_key[1], gesture_key[0]],  
        "queue3": [gesture_key[4], gesture_key[1], gesture_key[0]],  
        "queue4": [gesture_key[3], gesture_key[1], gesture_key[0]],  
        "queue6": [gesture_key[0]]
    }
    current_queue_name = None
    gesture_queue = []
    activated = False
    queue_start_time = None
    timeout = 5  
    volume_mode = False
    last_gesture = None
    # endregion

    while True:
        # region read frame
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Get window handle
        window = win32gui.FindWindow(None, window_name)
        # endregion

        # region timeout check queue
        # Check timeout at the beginning of the loop (if activated)
        if activated and queue_start_time is not None:
            if time.time() - queue_start_time > timeout:
                print("Time out! Canceling queue.")
                gesture_queue = []
                activated = False
                queue_start_time = None
                current_queue_name = None
        # endregion

        # region when tracking hands
        if results.multi_hand_landmarks:
            # Show window if currently hidden
            if not window_visible:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
                window_visible = True

            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # region Draw landmarks and Predict gesture
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = predict_gesture(hand_landmarks)
                # endregion

                # region trigger gesture
                if not volume_mode and not activated and last_gesture is None:
                    if current_gesture == gesture_key[6]:
                        activated = True
                        volume_mode = True
                        last_gesture = current_gesture
                        print("Switched to volume control mode!")
                        continue 
                if not activated and last_gesture is None:
                    if current_gesture == gesture_key[5]:
                        current_queue_name = "queue1"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated stop/turn off video!")
                        continue
                    elif current_gesture == gesture_key[1]:
                        current_queue_name = "queue2"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated open application!")
                        continue
                    elif current_gesture == gesture_key[4]:
                        current_queue_name = "queue3"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated next track!")
                        continue
                    elif current_gesture == gesture_key[3]:
                        current_queue_name = "queue4"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated previous track!")   
                        continue    
                elif volume_mode and activated and last_gesture != current_gesture:
                    if current_gesture == gesture_key[4]:
                        pyautogui.press('volumeup')
                        
                    elif current_gesture == gesture_key[3]:
                        pyautogui.press('volumedown')

                    elif current_gesture == gesture_key[5]:
                        volume_mode = False
                        activated = False
                        last_gesture = None
                        print("Turned off volume control mode!")
                    continue
                elif activated and gesture_queue and last_gesture is None:
                    if current_gesture == gesture_queue[0]:
                        gesture_queue.pop(0)
                        print(f"Correct gesture detected, remaining: {gesture_queue}")

                    if not gesture_queue:
                        if current_queue_name == "queue1":
                            send_play_pause()
                        elif current_queue_name == "queue2":
                            subprocess.Popen(['start', 'mswindowsmusic:'], shell=True)
                        elif current_queue_name == "queue3":
                            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, 0, 0)
                            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                        elif current_queue_name == "queue4":
                            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, 0, 0)
                            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)

                        activated = False
                        gesture_queue = []
                        current_queue_name = None
                        queue_start_time = None
                # endregion

                # region display recognized gesture
                gesture_name = GESTURES.get(current_gesture, "Unknown")
                y_pos = 30 + idx * 40  # Each hand is 40px apart vertically
                cv2.putText(frame, f"Hand {idx+1}: {gesture_name}", (10, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # endregion
        else:
            # Hide window if no hand detected
            if window_visible:
                win32gui.ShowWindow(window, win32con.SW_HIDE)
                window_visible = False
            last_gesture = None
        # endregion

        cv2.imshow(window_name, frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        with open('mode_config.json', 'r') as f:
            config = json.load(f)
            if config.get('current_mode') == 'SLIDE':
                print("Switching to slide control mode.")
                break
        time.sleep(0.05)

    cap.release()
    cv2.destroyAllWindows()

def control_slide():
    print(GESTURES)
    
    # region initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.9)
    mp_draw = mp.solutions.drawing_utils
    #endregion

    # region gui camera
    # Initialize camera
    cap = cv2.VideoCapture(0)

    # Create and position window without title bar and shadow
    window_name = 'Gesture Control'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    hwnd = win32gui.FindWindow(None, window_name)
    
    # Remove window border, title bar, and shadow
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style = style & ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | 
                     win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
    # Remove extended window styles (including shadow)
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style = ex_style & ~(win32con.WS_EX_DLGMODALFRAME | win32con.WS_EX_CLIENTEDGE | 
                           win32con.WS_EX_STATICEDGE | win32con.WS_EX_WINDOWEDGE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    
    # Get screen resolution
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # Set window size
    window_width = 320
    window_height = 240
    
    # Calculate position (e.g., top-right corner with 20px margin)
    pos_x = (screen_width - window_width) // 2
    pos_y = 20

    # Set window position and size
    win32gui.SetWindowPos(hwnd, 
                         win32con.HWND_TOPMOST,  # Changed to HWND_TOPMOST to keep window on top
                         pos_x, pos_y,
                         window_width, window_height,
                         win32con.SWP_SHOWWINDOW)
    #endregion

    # region Control variables
    window_visible = False
    gesture_key = list(GESTURES)
    # endregion

    # region test gesture
    queue_templates = {
        "queue1": [gesture_key[1], gesture_key[0]],
        "queue2": [gesture_key[1], gesture_key[0]]
    }
    current_queue_name = None
    gesture_queue = []
    activated = False
    queue_start_time = None
    timeout = 5  # seconds
    # endregion

    while True:
        # region read frame
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Get window handle
        window = win32gui.FindWindow(None, window_name)
        # endregion

        # region timeout check queue
        # Check timeout at the beginning of the loop (if activated)
        if activated and queue_start_time is not None:
            if time.time() - queue_start_time > timeout:
                print("Time out! Canceling queue.")
                gesture_queue = []
                activated = False
                queue_start_time = None
                current_queue_name = None
        # endregion

        # region when tracking hands
        if results.multi_hand_landmarks:
            # Show window if currently hidden
            if not window_visible:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
                window_visible = True

            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # region Draw landmarks and Predict gesture
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = predict_gesture(hand_landmarks)
                # endregion

                # region trigger gesture 
                if not activated:
                    if current_gesture == gesture_key[1]:
                        current_queue_name = "queue1"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated next slide")
                        continue
                    elif current_gesture == gesture_key[2]:
                        current_queue_name = "queue2"
                        gesture_queue = queue_templates[current_queue_name].copy()
                        activated = True
                        queue_start_time = time.time()
                        print("Activated previous slide!")
                        continue

                elif activated and gesture_queue:
                    if current_gesture == gesture_queue[0]:
                        gesture_queue.pop(0)
                        print(f"Correct gesture detected, remaining: {gesture_queue}")
                        time.sleep(0.2) 

                    if not gesture_queue:
                        if current_queue_name == "queue1":
                            if focus_powerpoint_slideshow():
                                win32api.keybd_event(win32con.VK_RIGHT, 0, 0, 0)
                                time.sleep(0.05)
                                win32api.keybd_event(win32con.VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)
                            else:
                                print("Could not find PowerPoint Slide Show window!")
                        elif current_queue_name == "queue2":
                            print("Correct gesture detected, going back!")
                            if focus_powerpoint_slideshow():
                                win32api.keybd_event(win32con.VK_LEFT, 0, 0, 0)
                                time.sleep(0.05)
                                win32api.keybd_event(win32con.VK_LEFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                            else:
                                print("Could not find PowerPoint Slide Show window!")

                        activated = False
                        gesture_queue = []
                        current_queue_name = None
                        queue_start_time = None
                # endregion

                # region display recognized gesture
                gesture_name = GESTURES.get(current_gesture, "Unknown")
                y_pos = 30 + idx * 40  # Each hand is 40px apart vertically
                cv2.putText(frame, f"Hand {idx+1}: {gesture_name}", (10, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # endregion
        else:
            # Hide window if no hand detected
            if window_visible:
                win32gui.ShowWindow(window, win32con.SW_HIDE)
                window_visible = False
            last_gesture = None
        # endregion

        cv2.imshow(window_name, frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        with open('mode_config.json', 'r') as f:
            config = json.load(f)
            if config.get('current_mode') == 'VIDEO':
                print("Switching to video control mode.")
                break
        time.sleep(0.05)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    while True:
        with open('mode_config.json', 'r') as f:
            config = json.load(f)
            current_mode = config.get('current_mode', 'VIDEO')

        if current_mode == 'VIDEO':
            GESTURES = get_gesture_mappings('VIDEO')    
            control_video()
        elif current_mode == 'SLIDE':
            GESTURES = get_gesture_mappings('SLIDE')
            control_slide()