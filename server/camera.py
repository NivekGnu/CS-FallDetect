import cv2
import mediapipe as mp
import time
import os
import threading

from collections import deque
from twilio.rest import Client
from voice import VoiceAssistant
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
AUTH_KEY = os.getenv("TWILIO_AUTH_KEY")
ACCT_SID = os.getenv("TWILIO_ACCT_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

class Camera:
    ALERT_COOLDOWN = 60  # seconds between alerts
    CONFIRMATION_FRAMES = 15  # number of consecutive frames to confirm fall
    LYING_DOWN_THRESHOLD = 0.1  # tune this

    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        self.draw = mp.solutions.drawing_utils
        self.capture = cv2.VideoCapture(0)
        self.horizontal_frames = 0
        self.last_alert_time = 0
        self.fall_active = False  # for /status endpoint
        self.client = Client(ACCT_SID, AUTH_KEY)  # replace with actual credentials
        self.voice_assistant = VoiceAssistant()


    def send_alert(self):
        threading.Thread(target=self._handle_fall_response, daemon=True).start()
        
    def _handle_fall_response(self):
        response = self.voice_assistant.respond_to_fall()
        if response == "emergency":
            self.client.messages.create(
                body="EMERGENCY SERVICES: Fall detected, user requested emergency help",
                from_=TWILIO_PHONE_NUMBER, to=MY_PHONE_NUMBER
            )
        elif response == "family":  # family
            self.client.messages.create(
                body="A family member has sent this message requesting help from a fall.",
                from_=TWILIO_PHONE_NUMBER, to=MY_PHONE_NUMBER
            )            
        elif response == "no_response":
            self.client.messages.create(
                body="Fall detected, but no response from user.",
                from_=TWILIO_PHONE_NUMBER, to=MY_PHONE_NUMBER
            )
        else:
            return

    def process(self):
        ret, frame = self.capture.read()
        if not ret:
            return None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            self.draw.draw_landmarks(
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
                shoulder_hip_diff < self.LYING_DOWN_THRESHOLD
                and hip_knee_diff < self.LYING_DOWN_THRESHOLD
            ) or aspect_ratio > 1.2

            if is_horizontal:
                self.horizontal_frames += 1
            else:
                self.horizontal_frames = 0
                self.fall_active = False

            if self.horizontal_frames >= self.CONFIRMATION_FRAMES:
                self.fall_active = True
                cv2.putText(
                    frame,
                    "FALL DETECTED!",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3,
                )

                if time.time() - self.last_alert_time >= self.ALERT_COOLDOWN:
                    self.send_alert()
                    self.last_alert_time = time.time()
            
        return frame
