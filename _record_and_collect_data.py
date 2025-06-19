import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time

# --- config ---
RECORD_DURATION_SECONDS = 30 # time recording duration
OUTPUT_VIDEO_DIR = 'recorded_gestures' # folder to save recorded videos
CSV_FILE_NAME = 'gesture_data_auto_record.csv' # name of the CSV file to save landmarks

# define MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# labels for gestures
gestures = {
    0: "Unknown", 
    1: "Closed_Fist",
    2: "Open_Palm",
    3: "Pointing_Up",
    4: "Thumb_Down",
    5: "Thumb_Up",
    6: "Victory",
    7: "ILoveYou"
}

# Create output video directory if it doesn't exist
if not os.path.exists(OUTPUT_VIDEO_DIR):
    os.makedirs(OUTPUT_VIDEO_DIR)
    print(f"folder '{OUTPUT_VIDEO_DIR}' created.")

# create header for CSV file
num_landmarks = 21
header = []
for i in range(num_landmarks):
    header.extend([f'x{i}', f'y{i}', f'z{i}'])
header.append('label')

# write header to CSV file if it doesn't exist
if not os.path.exists(CSV_FILE_NAME):
    with open(CSV_FILE_NAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print(f"File CSV '{CSV_FILE_NAME}' created with header.")
else:
    print(f"File CSV '{CSV_FILE_NAME}' already exists. Data will be appended.")

# Function to process recorded video and save landmarks to CSV
def process_recorded_video_and_save_landmarks(video_path, gesture_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Can't open video: {video_path}")
        return 0

    print(f"\nStarting processing video '{os.path.basename(video_path)}' for gesture '{gestures.get(gesture_id, 'N/A')}'...")
    collected_samples = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        # Change color from BGR (OpenCV) to RGB (MediaPipe)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the image with MediaPipe Hands
        results = hands.process(image)
        # Convert RGB back to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Check if any hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on the frame (optional)
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

        cv2.putText(image, f"Processing: {os.path.basename(video_path)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Gesture: {gestures.get(gesture_id, 'N/A')}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Frames processed: {frame_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Samples collected: {collected_samples}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Processing Recorded Video', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Finished processing video '{os.path.basename(video_path)}'. A total of {collected_samples} samples have been collected.")
    return collected_samples

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Can't open camera.")
        return

    total_samples_collected_overall = 0
    recording = False
    out = None # VideoWriter object

    print("--- Automatic Data Collection Mode ---")
    print("Select the gesture you want to record, then press 's' to start recording for 30 seconds.")
    print("Press 'q' to quit at any time.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1) 

        display_frame = frame.copy() 

        if not recording:
            # Display gesture options
            y_offset = 30
            for id, name in gestures.items():
                if id != 0:
                    cv2.putText(display_frame, f"Press {id} for: {name}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
                    y_offset += 30
            cv2.putText(display_frame, "Press 's' to START recording", (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            # Display remaining time while recording
            elapsed_time = time.time() - start_time
            remaining_time = max(0, RECORD_DURATION_SECONDS - elapsed_time)
            cv2.putText(display_frame, f"RECORDING: {gestures.get(current_gesture_id, 'N/A')}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(display_frame, f"Time Left: {remaining_time:.1f}s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # write frame to video object
            out.write(frame)

            if elapsed_time >= RECORD_DURATION_SECONDS:
                recording = False
                out.release()
                print(f"Finished recording video: {video_filename}")
                # After recording, automatically process this video
                samples_from_video = process_recorded_video_and_save_landmarks(video_filepath, current_gesture_id)
                total_samples_collected_overall += samples_from_video
                print(f"Total samples collected so far: {total_samples_collected_overall}")


        cv2.imshow('Live Recording & Data Collection', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif not recording and key in [ord(str(i)) for i in gestures if i != 0]:
            # Choose gesture
            current_gesture_id = int(chr(key))
            print(f"Selected gesture: {gestures[current_gesture_id]}")
            
            # Get frame dimensions
            height, width = display_frame.shape[:2]
            
            # Calculate text size to center it
            text = f"Selected: {gestures[current_gesture_id]}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            
            # Calculate position (center-bottom)
            text_x = (width - text_width) // 2  # Center horizontally
            text_y = height - 30  # 30 pixels from bottom
            
            # Draw text
            cv2.putText(display_frame, text, 
                        (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, (255, 0, 0), 2, cv2.LINE_AA)
            
            cv2.imshow('Live Recording & Data Collection', display_frame)
            cv2.waitKey(500) # Give user time to see selection
        elif key == ord('s') and not recording:
            if 'current_gesture_id' not in locals():
                print("Please select a gesture before pressing 's'!")
                continue

            # Start recording
            recording = True
            start_time = time.time()

            # Create a unique video filename
            timestamp = int(time.time())
            video_filename = f"{gestures[current_gesture_id].lower()}_{timestamp}.mp4"
            video_filepath = os.path.join(OUTPUT_VIDEO_DIR, video_filename)

            # Set up VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
            fps = cap.get(cv2.CAP_PROP_FPS) # Get FPS from camera
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(video_filepath, fourcc, fps, (width, height))
            print(f"Started recording for gesture {gestures[current_gesture_id]} to '{video_filepath}'...")


    cap.release()
    if out is not None:
        out.release() # Ensure VideoWriter is released if program exits early
    cv2.destroyAllWindows()
    print(f"\nData collection process completed. A total of {total_samples_collected_overall} samples have been saved to '{CSV_FILE_NAME}'.")
    print("You can now train the model with this file.")

if __name__ == "__main__":
    main()