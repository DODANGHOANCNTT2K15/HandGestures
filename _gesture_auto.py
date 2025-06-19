import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import joblib
import os # Add os library to check file existence

# --- Configuration ---
MODEL_PATH = 'gesture_recognition_model.h5' # Name of the saved model from step 1
SCALER_PATH = 'scaler.pkl'     # Name of the saved scaler from step 1

# Your gesture labels (MUST MATCH THE EXACT ORDER OF ID AND NAME USED IN TRAINING)
# Ensure IDs match your training data (0-7)
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

CONFIDENCE_THRESHOLD = 0.75 # Confidence threshold to display prediction (can be adjusted)

# --- Check and load model/scaler ---
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

# --- Initialize MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

def main():
    cap = cv2.VideoCapture(0) # Open default camera (0)

    if not cap.isOpened():
        print("Error: Cannot open camera. Please check webcam connection.")
        return

    print("Gesture recognition started. Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frame from camera. Exiting program.")
            break

        # Flip the frame horizontally for a natural (mirror-like) view
        frame = cv2.flip(frame, 1)

        # Convert color from BGR (OpenCV) to RGB (MediaPipe)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process image with MediaPipe Hands
        results = hands.process(image_rgb)

        # Convert color back to BGR for OpenCV display
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        current_gesture_display = "No Hand Detected"

        # Check if any hand is detected
        if results.multi_hand_landmarks:
            # Take the first detected hand for simplicity
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw landmarks and connections on the frame
            mp_draw.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract landmark coordinates into a flat list
            landmark_data = []
            for landmark in hand_landmarks.landmark:
                landmark_data.extend([landmark.x, landmark.y, landmark.z])

            # Ensure the number of features matches model input (21 landmarks * 3 coordinates = 63)
            if len(landmark_data) == 63:
                # Normalize input data using the trained scaler
                input_data_scaled = scaler.transform(np.array(landmark_data).reshape(1, -1))

                # Predict gesture using the loaded model
                prediction = model.predict(input_data_scaled, verbose=0)[0]
                predicted_class_id = np.argmax(prediction)
                confidence = np.max(prediction)

                # Display result only if confidence is high enough
                if confidence > CONFIDENCE_THRESHOLD:
                    predicted_label = GESTURE_LABELS.get(predicted_class_id, "Unknown Label")
                    current_gesture_display = f"{predicted_label} ({confidence:.2f})"
                else:
                    # If confidence is low, still display as Unknown
                    current_gesture_display = f"Unknown (Conf: {confidence:.2f})"
            else:
                current_gesture_display = "Error: Invalid Landmarks"

        # Display predicted gesture on the frame
        cv2.putText(image_bgr, f"Gesture: {current_gesture_display}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Show the frame
        cv2.imshow('Real-time Gesture Recognition (Simple)', image_bgr)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    print("Gesture recognition program has ended.")

if __name__ == "__main__":
    main()