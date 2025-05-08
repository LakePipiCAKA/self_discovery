import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import cv2
import face_recognition
from face_detection.face_detector import HailoFaceDetector
from camera.camera_interface import CameraInterface
from user_profiles import load_profiles


def compare_embeddings(known_embedding, new_embedding, tolerance=0.65):
    distance = face_recognition.face_distance([known_embedding], new_embedding)[0]
    return distance <= tolerance, distance


def recognize_live_face():
    profiles = load_profiles()
    known_embeddings = {
        uid: profile["facial_data"]["encodings"]
        for uid, profile in profiles.items()
        if profile["facial_data"]["encodings"]
    }

    if not known_embeddings:
        print("❌ No saved user embeddings found.")
        return

    camera = CameraInterface()
    face_detector = HailoFaceDetector(
        "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
    )

    print("🟢 Starting face recognition. Press 'q' to quit.")

    try:
        while True:
            frame = camera.get_frame()
            frame = cv2.flip(frame, 1)

            boxes = face_detector.detect_faces(frame)
            print(f"[DEBUG] Hailo detected {len(boxes)} face(s)")

            for box in boxes:
                if len(box) >= 4:
                    x, y, w, h = map(int, box[:4])

                    # Prepare face location in dlib format (top, right, bottom, left)
                    face_location = [(y, x + w, y + h, x)]

                    encodings = face_recognition.face_encodings(
                        frame, known_face_locations=face_location
                    )
                    if not encodings:
                        continue

                    new_embedding = encodings[0]
                    matched = False

                    for uid, embedding in known_embeddings.items():
                        match, distance = compare_embeddings(embedding, new_embedding)
                        if match:
                            name_label = f"{uid} ({distance:.2f})"
                            print(f"✅ Match: {name_label}")
                            cv2.putText(
                                frame,
                                name_label,
                                (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2,
                            )
                            matched = True
                            break

                    if not matched:
                        print("❓ Unknown face")
                        cv2.putText(
                            frame,
                            "Unknown",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2,
                        )

                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow("Live Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        camera.stop()
        face_detector.close()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass


if __name__ == "__main__":
    recognize_live_face()
