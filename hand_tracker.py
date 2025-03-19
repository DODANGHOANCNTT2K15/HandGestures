# hand_tracker.py
import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands, min_detection_confidence):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.results = None

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self.results

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_drawing.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
        )

    def is_open_hand(self, hand_landmarks, frame_height):
        index_tip_y = hand_landmarks.landmark[8].y * frame_height
        middle_tip_y = hand_landmarks.landmark[12].y * frame_height
        ring_tip_y = hand_landmarks.landmark[16].y * frame_height
        pinky_tip_y = hand_landmarks.landmark[20].y * frame_height
        wrist_y = hand_landmarks.landmark[0].y * frame_height
        return (index_tip_y < wrist_y and middle_tip_y < wrist_y and 
                ring_tip_y < wrist_y and pinky_tip_y < wrist_y)

    def is_fist(self, hand_landmarks, frame_height):
        index_tip_y = hand_landmarks.landmark[8].y * frame_height
        middle_tip_y = hand_landmarks.landmark[12].y * frame_height
        ring_tip_y = hand_landmarks.landmark[16].y * frame_height
        pinky_tip_y = hand_landmarks.landmark[20].y * frame_height
        index_base_y = hand_landmarks.landmark[5].y * frame_height
        middle_base_y = hand_landmarks.landmark[9].y * frame_height
        ring_base_y = hand_landmarks.landmark[13].y * frame_height
        pinky_base_y = hand_landmarks.landmark[17].y * frame_height
        return (index_tip_y >= index_base_y and middle_tip_y >= middle_base_y and 
                ring_tip_y >= ring_base_y and pinky_tip_y >= pinky_base_y)

    def is_palm_facing_camera(self, hand_landmarks, handedness):
        thumb_tip_x = hand_landmarks.landmark[4].x
        index_tip_x = hand_landmarks.landmark[8].x
        is_right_hand = handedness.classification[0].label == "Right"
        return (is_right_hand and thumb_tip_x < index_tip_x) or (not is_right_hand and thumb_tip_x > index_tip_x)

    def is_pointer_gesture(self, hand_landmarks, frame_height):
        index_tip_y = hand_landmarks.landmark[8].y * frame_height
        middle_tip_y = hand_landmarks.landmark[12].y * frame_height
        ring_tip_y = hand_landmarks.landmark[16].y * frame_height
        pinky_tip_y = hand_landmarks.landmark[20].y * frame_height
        index_base_y = hand_landmarks.landmark[5].y * frame_height
        middle_base_y = hand_landmarks.landmark[9].y * frame_height
        ring_base_y = hand_landmarks.landmark[13].y * frame_height
        pinky_base_y = hand_landmarks.landmark[17].y * frame_height
        wrist_y = hand_landmarks.landmark[0].y * frame_height
        return (index_tip_y < wrist_y and 
                middle_tip_y >= middle_base_y and 
                ring_tip_y >= ring_base_y and 
                pinky_tip_y >= pinky_base_y)

    def is_ok_gesture(self, hand_landmarks, frame_height):
        thumb_tip_x = hand_landmarks.landmark[4].x * frame_height
        thumb_tip_y = hand_landmarks.landmark[4].y * frame_height
        index_tip_x = hand_landmarks.landmark[8].x * frame_height
        index_tip_y = hand_landmarks.landmark[8].y * frame_height
        middle_tip_y = hand_landmarks.landmark[12].y * frame_height
        ring_tip_y = hand_landmarks.landmark[16].y * frame_height
        pinky_tip_y = hand_landmarks.landmark[20].y * frame_height
        wrist_y = hand_landmarks.landmark[0].y * frame_height
        
        # Khoảng cách giữa ngón cái và ngón trỏ nhỏ (tạo vòng tròn)
        distance_thumb_index = ((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2) ** 0.5
        return (distance_thumb_index < 30 and  # Ngưỡng khoảng cách
                middle_tip_y < wrist_y and ring_tip_y < wrist_y and pinky_tip_y < wrist_y)

    def get_index_tip_y(self, hand_landmarks, frame_height):
        return hand_landmarks.landmark[8].y * frame_height

    def close(self):
        self.hands.close()