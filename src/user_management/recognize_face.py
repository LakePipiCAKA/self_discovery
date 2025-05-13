# /home/taran/self_discovery/src/user_management/recognize_face.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import cv2
import face_recognition
from face_detection.face_detector import HailoFaceDetector
from camera.camera_interface import CameraInterface
from user_management.user_profiles import load_profiles

# Optional tunables
RECOGNITION_THRESHOLD = 0.6
POSTPROCESS_THRESHOLD = 0.3
DEBUG = True

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")


def load_user_profiles():
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def compare_embeddings(known_embedding, new_embedding):
    import numpy as np

    if new_embedding is None or known_embedding is None:
        return None, float("inf")
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
                face_image = frame[y : y + h, x : x + w]
                rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_face)

                label = "❓ Unknown face"
                if encodings:
                    embedding = encodings[0]
                    matches = []
                    for user_id, known in known_users.items():
                        match, dist = compare_embeddings(known, embedding)
                        if DEBUG:
                            print(f"[CHECK] {user_id}: dist={dist}, match={match}")
                        if match:
                            matches.append((user_id, dist))

                    if matches:
                        best_match = sorted(matches, key=lambda x: x[1])[0]
                        uid, score = best_match
                        if score < 0.45:
                            label = f"✅ Confirmed match: {uid} ({score})"
                        else:
                            label = f"⏳ Tentative match: {uid} ({score})"

                if DEBUG:
                    print(f"[BOX] x:{x} y:{y} w:{w} h:{h}")

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

    for user_id, known in known_users.items():
        match, dist = compare_embeddings(known, new_embedding)
        if match and dist < best_score:
            best_match = user_id
            best_score = dist

    return best_match


if __name__ == "__main__":
    recognize_live_face()
