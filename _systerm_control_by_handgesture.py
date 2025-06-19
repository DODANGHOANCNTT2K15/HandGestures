import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
import win32api
import win32con
import time
import os  
import joblib
import win32gui  

MODEL_PATH = 'gesture_recognition_model.h5'
SCALER_PATH = 'scaler.pkl' 

# Load the trained model and scaler
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

# Define gesture mappings
GESTURES = {
    1: "Closed_Fist",    # Pause
    2: "Open_Palm"       # Play
}

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

def control_systerm():
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.95,
        min_tracking_confidence=0.9)
    mp_draw = mp.solutions.drawing_utils

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
    
    # Control variables
    last_gesture = None
    gesture_cooldown = 1.0  # Seconds between gesture triggers
    last_trigger_time = 0
    window_visible = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Get window handle
        window = win32gui.FindWindow(None, window_name)

        if results.multi_hand_landmarks:
            # Show window if currently hidden
            if not window_visible:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
                window_visible = True
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Predict gesture
                current_gesture = predict_gesture(hand_landmarks)
                
                # Check if gesture should trigger action
                current_time = time.time()
                if (current_gesture in GESTURES and 
                    current_gesture != last_gesture and 
                    current_time - last_trigger_time > gesture_cooldown):
                    
                    # Trigger play/paused
                    send_play_pause()
                    last_trigger_time = current_time
                    last_gesture = current_gesture
                
                # Display recognized gesture
                gesture_name = GESTURES.get(current_gesture, "Unknown")
                cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            # Hide window if no hand detected
            if window_visible:
                win32gui.ShowWindow(window, win32con.SW_HIDE)
                window_visible = False
            last_gesture = None

        cv2.imshow(window_name, frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    control_systerm()