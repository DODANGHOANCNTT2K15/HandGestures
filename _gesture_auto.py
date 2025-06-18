import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import joblib
import os # Thêm thư viện os để kiểm tra sự tồn tại của file

# --- Cấu hình ---
MODEL_PATH = 'gesture_recognition_model.h5' # Tên mô hình đã lưu từ bước 1
SCALER_PATH = 'scaler.pkl'     # Tên scaler đã lưu từ bước 1

# Các nhãn cử chỉ của bạn (PHẢI KHỚP ĐÚNG THỨ TỰ ID VÀ TÊN KHI HUẤN LUYỆN)
# Đảm bảo các ID khớp với dữ liệu huấn luyện của bạn (0-7)
GESTURE_LABELS = {
    0: "Unknown",
    1: "Closed_Fist",
    2: "Open_Palm",
    3: "Pointing_Up",
    4: "Thumb_Down",
    5: "Thumb_Up",
    6: "Victory",
    7: "ILoveYou"
}

CONFIDENCE_THRESHOLD = 0.75 # Ngưỡng độ tin cậy để hiển thị dự đoán (có thể điều chỉnh)

# --- Kiểm tra và tải mô hình/scaler ---
if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    print(f"Lỗi: Không tìm thấy file mô hình ('{MODEL_PATH}') hoặc scaler ('{SCALER_PATH}').")
    print("Vui lòng chạy script 'train_model.py' trước để huấn luyện và lưu chúng.")
    exit()

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print(f"Đã tải thành công mô hình từ '{MODEL_PATH}' và scaler từ '{SCALER_PATH}'.")
except Exception as e:
    print(f"Lỗi khi tải mô hình hoặc scaler: {e}")
    print("Kiểm tra lại đường dẫn file và định dạng.")
    exit()

# --- Khởi tạo MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

def main():
    cap = cv2.VideoCapture(0) # Mở camera mặc định (0)

    if not cap.isOpened():
        print("Lỗi: Không thể mở camera. Vui lòng kiểm tra kết nối webcam.")
        return

    print("Bắt đầu nhận diện cử chỉ. Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc frame từ camera. Thoát chương trình.")
            break

        # Lật khung hình theo chiều ngang cho góc nhìn tự nhiên (như gương)
        frame = cv2.flip(frame, 1)

        # Chuyển đổi màu sắc từ BGR (OpenCV) sang RGB (MediaPipe)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Xử lý hình ảnh với MediaPipe Hands
        results = hands.process(image_rgb)

        # Chuyển đổi lại màu sắc về BGR để hiển thị với OpenCV
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        current_gesture_display = "No Hand Detected"

        # Kiểm tra xem có bàn tay nào được phát hiện không
        if results.multi_hand_landmarks:
            # Lấy thông tin bàn tay đầu tiên được phát hiện để đơn giản
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Vẽ các điểm mốc và kết nối lên khung hình
            mp_draw.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Trích xuất tọa độ điểm mốc thành một list phẳng
            landmark_data = []
            for landmark in hand_landmarks.landmark:
                landmark_data.extend([landmark.x, landmark.y, landmark.z])

            # Đảm bảo số lượng đặc trưng khớp với đầu vào của mô hình (21 điểm mốc * 3 tọa độ = 63)
            if len(landmark_data) == 63:
                # Chuẩn hóa dữ liệu đầu vào bằng scaler đã được huấn luyện
                input_data_scaled = scaler.transform(np.array(landmark_data).reshape(1, -1))

                # Dự đoán cử chỉ bằng mô hình đã tải
                prediction = model.predict(input_data_scaled, verbose=0)[0]
                predicted_class_id = np.argmax(prediction)
                confidence = np.max(prediction)

                # Hiển thị kết quả chỉ khi độ tin cậy đủ cao
                if confidence > CONFIDENCE_THRESHOLD:
                    predicted_label = GESTURE_LABELS.get(predicted_class_id, "Unknown Label")
                    current_gesture_display = f"{predicted_label} ({confidence:.2f})"
                else:
                    # Nếu độ tin cậy thấp, vẫn hiển thị là Unknown
                    current_gesture_display = f"Unknown (Conf: {confidence:.2f})"
            else:
                current_gesture_display = "Error: Invalid Landmarks"

        # Hiển thị cử chỉ dự đoán trên khung hình
        cv2.putText(image_bgr, f"Gesture: {current_gesture_display}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Hiển thị khung hình
        cv2.imshow('Real-time Gesture Recognition (Simple)', image_bgr)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng camera và đóng tất cả cửa sổ OpenCV
    cap.release()
    cv2.destroyAllWindows()
    print("Chương trình nhận diện cử chỉ đã kết thúc.")

if __name__ == "__main__":
    main()