import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time

# --- Cấu hình ---
RECORD_DURATION_SECONDS = 30 # Thời gian ghi hình mỗi cử chỉ
OUTPUT_VIDEO_DIR = 'recorded_gestures' # Thư mục lưu video đã quay
CSV_FILE_NAME = 'gesture_data_auto_record.csv' # Tên file CSV để lưu dữ liệu

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Các nhãn cử chỉ của bạn
gestures = {
    0: "Unknown", # Sẽ không thu thập trực tiếp
    1: "Closed_Fist",
    2: "Open_Palm",
    3: "Pointing_Up",
    4: "Thumb_Down",
    5: "Thumb_Up",
    6: "Victory",
    7: "ILoveYou"
}

# Tạo thư mục lưu video nếu chưa tồn tại
if not os.path.exists(OUTPUT_VIDEO_DIR):
    os.makedirs(OUTPUT_VIDEO_DIR)
    print(f"Thư mục '{OUTPUT_VIDEO_DIR}' đã được tạo.")

# Tạo header cho file CSV (21 điểm mốc * 3 tọa độ xyz = 63 cột, cộng thêm cột nhãn)
num_landmarks = 21
header = []
for i in range(num_landmarks):
    header.extend([f'x{i}', f'y{i}', f'z{i}'])
header.append('label')

# Ghi header vào file CSV nếu file chưa tồn tại
if not os.path.exists(CSV_FILE_NAME):
    with open(CSV_FILE_NAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print(f"File CSV '{CSV_FILE_NAME}' đã được tạo với header.")
else:
    print(f"File CSV '{CSV_FILE_NAME}' đã tồn tại. Dữ liệu sẽ được thêm vào cuối.")

def process_recorded_video_and_save_landmarks(video_path, gesture_id):
    """
    Xử lý một file video đã quay, trích xuất điểm mốc và lưu vào CSV.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Lỗi: Không thể mở video tại đường dẫn: {video_path}")
        return 0

    print(f"\nBắt đầu xử lý video '{os.path.basename(video_path)}' cho cử chỉ '{gestures.get(gesture_id, 'N/A')}'...")
    collected_samples = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        # Chuyển đổi BGR sang RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Xử lý hình ảnh với MediaPipe Hands
        results = hands.process(image)
        # Chuyển đổi lại RGB sang BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Kiểm tra xem có bàn tay nào được phát hiện không
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ điểm mốc lên khung hình (tùy chọn)
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmark_row = []
                for landmark in hand_landmarks.landmark:
                    landmark_row.extend([landmark.x, landmark.y, landmark.z])

                if len(landmark_row) == num_landmarks * 3:
                    landmark_row.append(gesture_id)
                    with open(CSV_FILE_NAME, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(landmark_row)
                    collected_samples += 1
                # else: # Không cần cảnh báo nếu bỏ qua, vì frame có thể không đủ rõ ràng
                #     print(f"Cảnh báo: Frame {frame_count} - Không đủ điểm mốc hợp lệ. Bỏ qua.")

        cv2.putText(image, f"Processing: {os.path.basename(video_path)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Gesture: {gestures.get(gesture_id, 'N/A')}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Frames processed: {frame_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Samples collected: {collected_samples}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Processing Recorded Video', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Đã xử lý xong video '{os.path.basename(video_path)}'. Tổng cộng {collected_samples} mẫu đã được thu thập.")
    return collected_samples


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Lỗi: Không thể mở camera. Vui lòng kiểm tra webcam.")
        return

    total_samples_collected_overall = 0
    recording = False
    out = None # Đối tượng VideoWriter

    print("--- Chế độ thu thập dữ liệu tự động ---")
    print("Chọn cử chỉ bạn muốn ghi hình, sau đó nhấn 's' để bắt đầu ghi hình 30 giây.")
    print("Nhấn 'q' để thoát bất cứ lúc nào.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1) # Lật khung hình cho tự nhiên

        display_frame = frame.copy() # Dùng bản sao để vẽ text

        if not recording:
            # Hiển thị các lựa chọn cử chỉ
            y_offset = 30
            for id, name in gestures.items():
                if id != 0:
                    cv2.putText(display_frame, f"Press {id} for: {name}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
                    y_offset += 30
            cv2.putText(display_frame, "Press 's' to START recording (after selecting gesture)", (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            # Hiển thị thời gian còn lại khi đang ghi hình
            elapsed_time = time.time() - start_time
            remaining_time = max(0, RECORD_DURATION_SECONDS - elapsed_time)
            cv2.putText(display_frame, f"RECORDING: {gestures.get(current_gesture_id, 'N/A')}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(display_frame, f"Time Left: {remaining_time:.1f}s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Ghi frame vào video
            out.write(frame)

            if elapsed_time >= RECORD_DURATION_SECONDS:
                recording = False
                out.release()
                print(f"Đã ghi hình xong video: {video_filename}")
                # Sau khi ghi xong, tự động xử lý video này
                samples_from_video = process_recorded_video_and_save_landmarks(video_filepath, current_gesture_id)
                total_samples_collected_overall += samples_from_video
                print(f"Tổng số mẫu đã thu thập cho đến nay: {total_samples_collected_overall}")


        cv2.imshow('Live Recording & Data Collection', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif not recording and key in [ord(str(i)) for i in gestures if i != 0]:
            # Người dùng chọn cử chỉ
            current_gesture_id = int(chr(key))
            print(f"Đã chọn cử chỉ: {gestures[current_gesture_id]}")
            cv2.putText(display_frame, f"Selected: {gestures[current_gesture_id]}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow('Live Recording & Data Collection', display_frame)
            cv2.waitKey(500) # Cho người dùng thấy lựa chọn
        elif key == ord('s') and not recording:
            if 'current_gesture_id' not in locals():
                print("Vui lòng chọn cử chỉ trước khi bấm 's'!")
                continue

            # Bắt đầu ghi hình
            recording = True
            start_time = time.time()
            
            # Tạo tên file video duy nhất
            timestamp = int(time.time())
            video_filename = f"{gestures[current_gesture_id].lower()}_{timestamp}.mp4"
            video_filepath = os.path.join(OUTPUT_VIDEO_DIR, video_filename)

            # Cài đặt VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec cho .mp4
            fps = cap.get(cv2.CAP_PROP_FPS) # Lấy FPS từ camera
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(video_filepath, fourcc, fps, (width, height))
            print(f"Bắt đầu ghi hình cho cử chỉ {gestures[current_gesture_id]} vào '{video_filepath}'...")


    cap.release()
    if out is not None:
        out.release() # Đảm bảo VideoWriter được giải phóng nếu chương trình thoát sớm
    cv2.destroyAllWindows()
    print(f"\nQuá trình thu thập dữ liệu hoàn tất. Tổng cộng {total_samples_collected_overall} mẫu đã được lưu vào '{CSV_FILE_NAME}'.")
    print("Bây giờ bạn có thể huấn luyện mô hình với file này.")

if __name__ == "__main__":
    main()