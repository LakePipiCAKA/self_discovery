import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import cv2
import face_recognition
import numpy as np
from face_detection.face_detector import HailoFaceDetector
from camera.camera_interface import CameraInterface
from user_management.user_profiles import load_profiles

# Tunables
RECOGNITION_THRESHOLD = 0.6
DEBUG = True

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")


def load_user_profiles():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def compare_embeddings(known_embedding, new_embedding):
    distance = face_recognition.face_distance([known_embedding], new_embedding)[0]
    match = distance < RECOGNITION_THRESHOLD
    return match, round(float(distance), 2)


def recognize_live_face():
    print("🟢 Starting face recognition. Press 'q' to quit.")
    profiles = load_user_profiles()
    known_users = {
        user_id: data["facial_data"]["encodings"]
        for user_id, data in profiles.items()
        if data.get("facial_data") and data["facial_data"].get("encodings")
    }

    camera = CameraInterface()
    detector = HailoFaceDetector("models/hailo/yolov5s_personface_h8l.hef")

    frame_count = 0

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                print("Camera frame failed")
                break

            detections = detector.detect_faces(frame)
            if DEBUG:
                print(f"[DEBUG] Hailo detected {len(detections)} box(es)")

            for x, y, w, h, score in detections:
                frame_count += 1
                label = "😴 Skipped frame"

                # Run recognition every 5th frame
                if frame_count % 5 == 0:
                    face_image = frame[y : y + h, x : x + w]
                    small_face = cv2.resize(face_image, (0, 0), fx=0.5, fy=0.5)
                    rgb_face = cv2.cvtColor(small_face, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(rgb_face)

                    if encodings:
                        embedding = encodings[0]
                        matches = []

                        for user_id, known_list in known_users.items():
                            for idx, known in enumerate(known_list):
                                match, dist = compare_embeddings(known, embedding)
                                if DEBUG:
                                    print(
                                        f"[{user_id} #{idx+1}] dist={dist}, match={match}"
                                    )
                                if match:
                                    matches.append((user_id, dist))

                        if matches:
                            uid, best = sorted(matches, key=lambda x: x[1])[0]
                            label = f"✅ {uid} ({best})"
                        else:
                            label = "❓ Unknown face"
                    else:
                        label = "❌ No encoding"

                # Draw results
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            cv2.imshow("Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.stop()
        detector.close()
        cv2.destroyAllWindows()


def recognize_face(face_img_bgr):
    profiles = load_user_profiles()
    known_users = {
        user_id: data["facial_data"]["encodings"]
        for user_id, data in profiles.items()
        if data.get("facial_data") and data["facial_data"].get("encodings")
    }

    rgb_face = cv2.cvtColor(face_img_bgr, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_face)

    if not encodings:
        return None

    new_embedding = encodings[0]
    best_match = None
    best_score = float("inf")

    for user_id, known_list in known_users.items():
        for known in known_list:
            match, dist = compare_embeddings(known, new_embedding)
            if match and dist < best_score:
                best_match = user_id
                best_score = dist

    return best_match


if __name__ == "__main__":
    recognize_live_face()
