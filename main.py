import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1)

fall_detected = False
fall_time = None
last_alert_time = 0
ALERT_COOLDOWN = 10  # seconds between alerts

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
        mp_draw.draw_landmarks(frame, results.pose_landmarks,
                               mp.solutions.pose.POSE_CONNECTIONS)

        # Get key landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        # Average shoulder and hip Y positions
        # Note: Y increases downward in image coordinates
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_y = (left_hip.y + right_hip.y) / 2

        # Calculate vertical difference
        vertical_diff = abs(shoulder_y - hip_y)

        # If shoulders and hips are at similar height = person is horizontal
        if vertical_diff < 0.1:
            if not fall_detected:
                fall_detected = True
                fall_time = time.time()
            cv2.putText(frame, "FALL DETECTED!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            if time.time() - last_alert_time >= ALERT_COOLDOWN:
                send_alert()
                last_alert_time = time.time()
        else:
            fall_detected = False

    cv2.imshow('Fall Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()