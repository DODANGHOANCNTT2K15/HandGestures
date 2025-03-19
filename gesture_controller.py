# gesture_controller.py
import time

class GestureController:
    def __init__(self, gesture_timeout):
        self.was_fist = False
        self.gesture_enabled = False
        self.was_both_open = False
        self.both_open_start_time = 0
        self.toggle_triggered = False
        self.gesture_timeout = gesture_timeout
        self.volume_mode = False
        self.was_ok_gesture = False
        self.ok_gesture_start_time = 0
        self.volume_toggle_triggered = False
        self.last_volume_adjust_time = 0

    def update_gestures(self, hands_detected, hand_tracker, frame_height, on_toggle, on_space, on_volume_adjust, on_volume_toggle):
        text_lines = []
        current_time = time.time()

        if hands_detected and hands_detected.multi_hand_landmarks:
            hands_count = len(hands_detected.multi_hand_landmarks)

            # Xử lý chế độ âm lượng trước (ưu tiên khi volume_mode = True)
            if self.volume_mode and hands_count == 2:
                right_hand = None
                left_hand = None
                for idx, hand_landmarks in enumerate(hands_detected.multi_hand_landmarks):
                    handedness = hands_detected.multi_handedness[idx]
                    if handedness.classification[0].label == "Right":
                        right_hand = hand_landmarks
                    else:
                        left_hand = hand_landmarks

                if right_hand and left_hand:
                    right_open = hand_tracker.is_open_hand(right_hand, frame_height)
                    right_fist = hand_tracker.is_fist(right_hand, frame_height)
                    left_open = hand_tracker.is_open_hand(left_hand, frame_height)
                    left_fist = hand_tracker.is_fist(left_hand, frame_height)

                    if right_open and left_fist and (current_time - self.last_volume_adjust_time >= 0.5):
                        on_volume_adjust("increase")
                        text_lines.append("Am luong: Tang")
                        self.last_volume_adjust_time = current_time
                    elif right_fist and left_open and (current_time - self.last_volume_adjust_time >= 0.5):
                        on_volume_adjust("decrease")
                        text_lines.append("Am luong: Giam")
                        self.last_volume_adjust_time = current_time

            # Chỉ xử lý Space khi không ở chế độ âm lượng
            elif hands_count == 2 and not self.volume_mode:
                hand1_landmarks = hands_detected.multi_hand_landmarks[0]
                hand2_landmarks = hands_detected.multi_hand_landmarks[1]
                hand1_handedness = hands_detected.multi_handedness[0]
                hand2_handedness = hands_detected.multi_handedness[1]

                both_open_and_facing = (
                    hand_tracker.is_open_hand(hand1_landmarks, frame_height) and
                    hand_tracker.is_open_hand(hand2_landmarks, frame_height) and
                    hand_tracker.is_palm_facing_camera(hand1_landmarks, hand1_handedness) and
                    hand_tracker.is_palm_facing_camera(hand2_landmarks, hand2_handedness)
                )

                if both_open_and_facing:
                    if not self.was_both_open:
                        self.both_open_start_time = current_time
                    elif (current_time - self.both_open_start_time >= self.gesture_timeout and 
                          not self.toggle_triggered):
                        previous_state = self.gesture_enabled
                        self.gesture_enabled = not self.gesture_enabled
                        self.toggle_triggered = True
                        text_lines.append(f"Cu chi Space: {'Da kich hoat' if self.gesture_enabled else 'Da tat'}")
                        on_toggle(self.gesture_enabled, previous_state)
                else:
                    self.both_open_start_time = 0
                    self.toggle_triggered = False
                self.was_both_open = both_open_and_facing

            # Xử lý từng tay
            for idx, hand_landmarks in enumerate(hands_detected.multi_hand_landmarks):
                handedness = hands_detected.multi_handedness[idx]
                is_open = hand_tracker.is_open_hand(hand_landmarks, frame_height)
                is_fist = hand_tracker.is_fist(hand_landmarks, frame_height)
                palm_facing = hand_tracker.is_palm_facing_camera(hand_landmarks, handedness)
                is_ok = hand_tracker.is_ok_gesture(hand_landmarks, frame_height)

                if idx == 0:
                    text_lines.append(f"Tay {'phải' if handedness.classification[0].label == 'Right' else 'trái'}: " +
                                     ("Tay xoe" if is_open else "Tay nam" if is_fist else "OK" if is_ok else "Tay khong nam"))
                    text_lines.append("Long ban tay vao cam" if palm_facing else "Long ban tay ra ngoai")

                # Toggle chế độ Space (nắm tay)
                if self.gesture_enabled and is_fist and palm_facing and not self.was_fist:
                    text_lines.append("Da gui phim K")
                    on_space()
                self.was_fist = is_fist and palm_facing

                # Toggle chế độ âm lượng (OK gesture)
                if hands_count == 1 and is_ok:
                    if not self.was_ok_gesture:
                        self.ok_gesture_start_time = current_time
                    elif (current_time - self.ok_gesture_start_time >= 0.5 and 
                          not self.volume_toggle_triggered):
                        previous_volume_state = self.volume_mode
                        self.volume_mode = not self.volume_mode
                        self.volume_toggle_triggered = True
                        text_lines.append(f"Che do am luong: {'Da kich hoat' if self.volume_mode else 'Da tat'}")
                        on_volume_toggle(self.volume_mode, previous_volume_state)
                else:
                    self.ok_gesture_start_time = 0
                    self.volume_toggle_triggered = False
                self.was_ok_gesture = is_ok

        else:
            self.reset_state()

        text_lines.append(f"Trang thai Space: {'Da kich hoat' if self.gesture_enabled else 'Chua kich hoat'}")
        text_lines.append(f"Trang thai Am luong: {'Da kich hoat' if self.volume_mode else 'Chua kich hoat'}")
        return text_lines

    def reset_state(self):
        self.was_fist = False
        self.was_both_open = False
        self.both_open_start_time = 0
        self.toggle_triggered = False
        self.was_ok_gesture = False
        self.ok_gesture_start_time = 0
        self.volume_toggle_triggered = False
        self.last_volume_adjust_time = 0