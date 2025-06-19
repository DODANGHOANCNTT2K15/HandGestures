import cv2
import mediapipe as mp
import time
import win32gui  # type: ignore
import win32con  # type: ignore

def popup_window(name_window="Media Player"):
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Variables to control FPS and window state
    desired_fps = 24
    frame_delay = 1 / desired_fps
    window_visible = False

    while True:
        frame_start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame with MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Get window handle
        window = win32gui.FindWindow(None, name_window) 
        
        # Check if hand is detected
        if results.multi_hand_landmarks:
            # Show window if currently hidden
            if not window_visible:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
                window_visible = True
        else:
            # Hide window if no hand detected
            if window_visible:
                win32gui.ShowWindow(window, win32con.SW_HIDE)
                window_visible = False

        # Calculate delay to maintain FPS
        processing_time = time.time() - frame_start_time
        delay = max(1, int((frame_delay - processing_time) * 1000))

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            # Show window before exiting
            window = win32gui.FindWindow(None, name_window)
            if window:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
            break

    cap.release()
    cv2.destroyAllWindows()

# if __name__ == "__main__":
#     popup_window("Gesture Control")