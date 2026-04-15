import cv2
import mediapipe as mp
import time

from collections import deque

mp_pose = mp.solutions.pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

horizontal_frames = 0
last_alert_time = 0
hip_history = deque(maxlen=10)  # last 10 frames of hip_y

ALERT_COOLDOWN = 30  # seconds between alerts
CONFIRMATION_FRAMES = 15  # number of consecutive frames to confirm fall
LYING_DOWN_THRESHOLD = 0.1  # tune this

def send_alert():
    print("FALL DETECTED!")
    print("SENDING SMS MESSAGE")


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        mp_draw.draw_landmarks(
            frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )

        # Get key landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
        right_knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE]

        # Average shoulder and hip Y positions
        # Note: Y increases downward in image coordinates
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_y = (left_hip.y + right_hip.y) / 2
        knee_y = (left_knee.y + right_knee.y) / 2

        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]
        bbox_width = max(xs) - min(xs)
        bbox_height = max(ys) - min(ys)
        aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0

        # Calculate vertical difference
        shoulder_hip_diff = abs(shoulder_y - hip_y)
        hip_knee_diff = abs(hip_y - knee_y)

        # Determine if person is horizontal and fell fast
        is_horizontal = (
            shoulder_hip_diff < LYING_DOWN_THRESHOLD
            and hip_knee_diff < LYING_DOWN_THRESHOLD
        ) or aspect_ratio > 1.2

        if is_horizontal:
            horizontal_frames += 1
        else:
            horizontal_frames = 0

        if horizontal_frames >= CONFIRMATION_FRAMES:
            cv2.putText(
                frame,
                "FALL DETECTED!",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3,
            )

            if time.time() - last_alert_time >= ALERT_COOLDOWN:
                send_alert()
                last_alert_time = time.time()

    cv2.imshow("Fall Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
