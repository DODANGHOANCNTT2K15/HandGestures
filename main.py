import cv2
import mediapipe as mp
import time
import win32gui
import win32con

def popup_window():
    # Khởi tạo MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # Khởi tạo webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Biến để kiểm soát FPS và trạng thái cửa sổ
    desired_fps = 24
    frame_delay = 1/desired_fps
    window_visible = False

    while True:
        frame_start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        # Xử lý frame với MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Lấy handle của cửa sổ
        window = win32gui.FindWindow(None, "Media Player") 
        
        # Kiểm tra có phát hiện tay không
        if results.multi_hand_landmarks:
            # Hiện cửa sổ nếu đang ẩn
            if not window_visible:
                win32gui.ShowWindow(window, win32con.SW_SHOW)
                window_visible = True
        else:
            # Ẩn cửa sổ nếu không phát hiện tay
            if window_visible:
                win32gui.ShowWindow(window, win32con.SW_HIDE)
                window_visible = False

        # Tính toán delay để duy trì FPS
        processing_time = time.time() - frame_start_time
        delay = max(1, int((frame_delay - processing_time) * 1000))

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    popup_window()