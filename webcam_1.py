# import cv2
# import tkinter as tk
# from PIL import Image, ImageTk
# import mediapipe as mp
# import pyautogui
# import time
# import winsound

# class WebcamApp:
#     def __init__(self, window, window_title):
#         self.window = window
#         self.window.title(window_title)

#         # Thử mở webcam với CAP_DSHOW
#         self.cap = None
#         for i in range(3):  # Thử index 0, 1, 2
#             self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
#             if self.cap.isOpened():
#                 print(f"Đã mở webcam tại index {i}")
#                 break
#         if not self.cap or not self.cap.isOpened():
#             print("Không thể mở webcam. Kiểm tra kết nối hoặc driver.")
#             exit()

#         # Khởi tạo Mediapipe Hands
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
#         self.mp_drawing = mp.solutions.drawing_utils

#         # Biến trạng thái
#         self.was_fist = False  # Tay có nắm trước đó không
#         self.gesture_enabled = False  # Tính năng Space có được kích hoạt không
#         self.was_both_open = False  # Cả 2 tay có xòe trước đó không
#         self.both_open_start_time = 0  # Thời điểm bắt đầu phát hiện 2 tay xòe
#         self.toggle_triggered = False  # Đã toggle trong lần giữ này chưa

#         self.canvas = tk.Label(window)
#         self.canvas.pack()

#         self.delay = 10
#         self.update()

#         self.btn_quit = tk.Button(window, text="Thoát", command=self.quit)
#         self.btn_quit.pack()

#         self.window.mainloop()

#     def is_open_hand(self, hand_landmarks, frame_height):
#         index_tip = hand_landmarks.landmark[8]  # Đầu ngón trỏ
#         middle_tip = hand_landmarks.landmark[12]  # Đầu ngón giữa
#         ring_tip = hand_landmarks.landmark[16]  # Đầu ngón áp út
#         pinky_tip = hand_landmarks.landmark[20]  # Đầu ngón út
#         wrist = hand_landmarks.landmark[0]  # Cổ tay

#         index_y = index_tip.y * frame_height
#         middle_y = middle_tip.y * frame_height
#         ring_y = ring_tip.y * frame_height
#         pinky_y = pinky_tip.y * frame_height
#         wrist_y = wrist.y * frame_height

#         if (index_y < wrist_y and middle_y < wrist_y and 
#             ring_y < wrist_y and pinky_y < wrist_y):
#             return True
#         return False

#     def is_fist(self, hand_landmarks, frame_height):
#         index_tip = hand_landmarks.landmark[8]  # Đầu ngón trỏ
#         middle_tip = hand_landmarks.landmark[12]  # Đầu ngón giữa
#         ring_tip = hand_landmarks.landmark[16]  # Đầu ngón áp út
#         pinky_tip = hand_landmarks.landmark[20]  # Đầu ngón út
#         index_base = hand_landmarks.landmark[5]  # Gốc ngón trỏ
#         middle_base = hand_landmarks.landmark[9]  # Gốc ngón giữa
#         ring_base = hand_landmarks.landmark[13]  # Gốc ngón áp út
#         pinky_base = hand_landmarks.landmark[17]  # Gốc ngón út

#         index_tip_y = index_tip.y * frame_height
#         middle_tip_y = middle_tip.y * frame_height
#         ring_tip_y = ring_tip.y * frame_height
#         pinky_tip_y = pinky_tip.y * frame_height
#         index_base_y = index_base.y * frame_height
#         middle_base_y = middle_base.y * frame_height
#         ring_base_y = ring_base.y * frame_height
#         pinky_base_y = pinky_base.y * frame_height

#         if (index_tip_y >= index_base_y and middle_tip_y >= middle_base_y and 
#             ring_tip_y >= ring_base_y and pinky_tip_y >= pinky_base_y):
#             return True
#         return False

#     def is_palm_facing_camera(self, hand_landmarks, handedness):
#         thumb_tip = hand_landmarks.landmark[4]  # Đầu ngón cái
#         index_tip = hand_landmarks.landmark[8]  # Đầu ngón trỏ

#         is_right_hand = handedness.classification[0].label == "Right"

#         if is_right_hand and thumb_tip.x < index_tip.x:
#             return True
#         if not is_right_hand and thumb_tip.x > index_tip.x:
#             return True
#         return False

#     def update(self):
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.flip(frame, 1)
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = self.hands.process(rgb_frame)

#             both_open_and_facing = False

#             if results.multi_hand_landmarks:
#                 hands_count = len(results.multi_hand_landmarks)

#                 # Kiểm tra nếu có đủ 2 tay xòe và lòng bàn tay hướng vào camera để toggle
#                 if hands_count == 2:
#                     hand1_landmarks = results.multi_hand_landmarks[0]
#                     hand2_landmarks = results.multi_hand_landmarks[1]
#                     hand1_handedness = results.multi_handedness[0]
#                     hand2_handedness = results.multi_handedness[1]

#                     hand1_open = self.is_open_hand(hand1_landmarks, frame.shape[0])
#                     hand2_open = self.is_open_hand(hand2_landmarks, frame.shape[0])
#                     hand1_facing = self.is_palm_facing_camera(hand1_landmarks, hand1_handedness)
#                     hand2_facing = self.is_palm_facing_camera(hand2_landmarks, hand2_handedness)

#                     both_open_and_facing = hand1_open and hand2_open and hand1_facing and hand2_facing

#                     # Kiểm tra thời gian giữ 2 tay xòe
#                     current_time = time.time()
#                     if both_open_and_facing:
#                         if not self.was_both_open:
#                             self.both_open_start_time = current_time  # Bắt đầu đếm thời gian
#                         elif (current_time - self.both_open_start_time >= 1 and 
#                               not self.toggle_triggered):  # Giữ đủ 1 giây và chưa toggle
#                             previous_state = self.gesture_enabled
#                             self.gesture_enabled = not self.gesture_enabled
#                             self.toggle_triggered = True  # Đánh dấu đã toggle
#                             status = "Da kich hoat" if self.gesture_enabled else "Da tat"
#                             cv2.putText(frame, f"Cu chi Space: {status}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
#                             # Phát âm thanh thông báo
#                             if self.gesture_enabled and not previous_state:  # Khi bật
#                                 winsound.Beep(1000, 200)  # Tần số 1000Hz, dài 200ms
#                             elif not self.gesture_enabled and previous_state:  # Khi tắt
#                                 winsound.Beep(500, 200)   # Tần số 500Hz, dài 200ms
#                     else:
#                         self.both_open_start_time = 0  # Reset thời gian
#                         self.toggle_triggered = False  # Reset toggle khi không còn 2 tay

#                 # Xử lý từng tay để phát hiện nắm tay
#                 for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
#                     self.mp_drawing.draw_landmarks(
#                         frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
#                         self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
#                         self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
#                     )
#                     handedness = results.multi_handedness[idx]

#                     is_open = self.is_open_hand(hand_landmarks, frame.shape[0])
#                     is_fist = self.is_fist(hand_landmarks, frame.shape[0])
#                     palm_facing = self.is_palm_facing_camera(hand_landmarks, handedness)

#                     if is_open:
#                         cv2.putText(frame, "Tay xoe", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#                     elif is_fist:
#                         cv2.putText(frame, "Tay nam", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#                     else:
#                         cv2.putText(frame, "Tay khong nam", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#                     if palm_facing:
#                         cv2.putText(frame, "Long ban tay vao cam", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
#                     else:
#                         cv2.putText(frame, "Long ban tay ra ngoai", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

#                     # Nhấn Space khi nắm tay và tính năng đã kích hoạt
#                     if self.gesture_enabled and is_fist and palm_facing and not self.was_fist:
#                         cv2.putText(frame, "Space da nhan", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
#                         pyautogui.press("space")

#                     # Cập nhật trạng thái nắm tay
#                     self.was_fist = is_fist and palm_facing

#                 # Cập nhật trạng thái toggle cho 2 tay
#                 self.was_both_open = both_open_and_facing
#             else:
#                 # Reset trạng thái khi không có tay
#                 self.was_fist = False
#                 self.was_both_open = False
#                 self.both_open_start_time = 0
#                 self.toggle_triggered = False

#             # Hiển thị trạng thái tính năng Space
#             status = "Da kich hoat" if self.gesture_enabled else "Chua kich hoat"
#             cv2.putText(frame, f"Trang thai Space: {status}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             self.canvas.imgtk = imgtk
#             self.canvas.configure(image=imgtk)
#         self.window.after(self.delay, self.update)

#     def quit(self):
#         if self.cap and self.cap.isOpened():
#             self.cap.release()
#         self.hands.close()
#         self.window.quit()

# root = tk.Tk()
# app = WebcamApp(root, "Webcam Trực Tiếp với Tracking Tay")