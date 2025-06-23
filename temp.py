import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import joblib
import os
import time # Thêm để sử dụng time.sleep

# --- Cấu hình đường dẫn đến file mô hình và scaler ---
MODEL_PATH = 'gesture_recognition_model.h5'
SCALER_PATH = 'scaler.pkl'

# --- Định nghĩa các nhãn cử chỉ ---
# Đảm bảo các số index này (1, 2, 3...) khớp với cách bạn đã mã hóa nhãn khi huấn luyện mô hình.
# Nếu nhãn trong mô hình của bạn bắt đầu từ 0, hãy điều chỉnh cho phù hợp.
# Ví dụ: nếu mô hình dự đoán đầu ra là 0, 1, 2, 3, 4, 5, 6 thì bạn nên dùng GESTURE_LABELS = {0: "Closed_Fist", ...}
GESTURE_LABELS = {
    1: "Closed_Fist",   # Giả định cử chỉ đầu tiên (thường là 0) là Closed_Fist
    2: "Open_Palm",
    3: "Pointing_Up",
    4: "Thumb_Down",
    5: "Thumb_Up",
    6: "Victory",
    7: "ILoveYou"
}

# --- Tải mô hình học sâu và bộ chuẩn hóa (scaler) ---
if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    print(f"Lỗi: Không tìm thấy file mô hình ('{MODEL_PATH}') hoặc scaler ('{SCALER_PATH}').")
    print("Vui lòng đảm bảo bạn đã chạy chương trình huấn luyện mô hình (ví dụ: 'training_model.py') để tạo ra chúng.")
    exit()

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH) # Sử dụng joblib.load() như bạn đã lưu
    print(f"Đã tải mô hình thành công từ '{MODEL_PATH}' và scaler từ '{SCALER_PATH}'.")
except Exception as e:
    print(f"Lỗi khi tải mô hình hoặc scaler: {e}")
    print("Vui lòng kiểm tra đường dẫn file và định dạng.")
    exit()

# --- Khởi tạo MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # Chỉ nhận diện 1 bàn tay để đơn giản
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

# --- Hàm dự đoán cử chỉ ---
def predict_gesture(landmarks):
    """
    Chuyển đổi các mốc (landmarks) của bàn tay thành định dạng đầu vào của mô hình
    và dự đoán cử chỉ.
    """
    # Làm phẳng dữ liệu mốc thành mảng 1D (x, y, z cho mỗi mốc)
    row = []
    for landmark in landmarks.landmark:
        row.extend([landmark.x, landmark.y, landmark.z])
    
    # Chuẩn hóa các đặc trưng bằng scaler đã tải
    # Đảm bảo số lượng đặc trưng khớp với scaler của bạn
    try:
        if len(row) != scaler.n_features_in_:
            # Điều này xảy ra nếu bạn huấn luyện mô hình với số lượng mốc/chiều khác nhau
            print(f"Cảnh báo: Số lượng đặc trưng không khớp giữa dữ liệu hiện tại ({len(row)}) và scaler ({scaler.n_features_in_}). Bỏ qua dự đoán.")
            return -1 # Trả về giá trị đặc biệt để biểu thị lỗi
        
        scaled_row = scaler.transform([row])
        
        # Dự đoán bằng mô hình
        prediction = model.predict(scaled_row)
        predicted_class_index = np.argmax(prediction[0])
        confidence = np.max(prediction[0])
        
        # Bạn có thể thêm ngưỡng tin cậy ở đây nếu muốn
        # if confidence < 0.7:
        #     return -1 # hoặc một giá trị đặc biệt cho "không chắc chắn"
            
        return predicted_class_index
    except Exception as e:
        print(f"Lỗi trong quá trình predict_gesture: {e}")
        return -1 # Trả về giá trị đặc biệt khi có lỗi

# --- Khởi tạo Webcam ---
cap = cv2.VideoCapture(0) # 0 là webcam mặc định

if not cap.isOpened():
    print("Lỗi: Không thể mở webcam. Vui lòng kiểm tra kết nối webcam hoặc quyền truy cập.")
    exit()

print("Bắt đầu nhận diện cử chỉ tay. Nhấn 'q' để thoát.")

# --- Vòng lặp chính để nhận diện và hiển thị ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Không thể đọc frame từ webcam. Thoát chương trình.")
        break

    # Lật ngược frame để hiển thị tự nhiên hơn (như gương)
    frame = cv2.flip(frame, 1)

    # Chuyển đổi màu từ BGR sang RGB cho MediaPipe
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Xử lý hình ảnh với MediaPipe Hands
    results = hands.process(image_rgb)

    current_gesture_name = "Unknown"  # Biến để lưu tên cử chỉ hiện tại

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Vẽ các mốc bàn tay và kết nối lên frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Dự đoán cử chỉ
            predicted_index = predict_gesture(hand_landmarks)
            
            # Lấy tên cử chỉ từ dictionary
            if predicted_index != -1: # Nếu dự đoán thành công
                current_gesture_name = GESTURE_LABELS.get(predicted_index, "Không xác định")
            else:
                current_gesture_name = "Lỗi/Không rõ"
            
            # Chỉ xử lý một bàn tay và hiển thị cử chỉ cho bàn tay đó
            break 
    
    # Hiển thị cử chỉ nhận diện được trên frame
    cv2.putText(frame, f"{current_gesture_name}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Hiển thị frame lên cửa sổ
    cv2.imshow('Nhan dien cu chi tay co ban', frame)

    # Nhấn 'q' để thoát chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Giải phóng tài nguyên ---
cap.release()
cv2.destroyAllWindows()
hands.close()
print("Chương trình nhận diện cử chỉ cơ bản đã kết thúc.")