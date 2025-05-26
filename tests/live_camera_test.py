# /home/taran/self_discovery/tests/live_camera_test.py
from picamera2 import Picamera2
import cv2
import numpy as np
import time
from pathlib import Path
import sys

# Add project root to sys.path to allow import from src
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.face_detection.face_detector import HailoFaceDetector

HEF_PATH = ROOT_DIR / "models/hailo/yolov5s_personface_h8l.hef"


class CameraInterface:
    def __init__(self, resolution=(640, 480)):
        self.picam = Picamera2()
        self.resolution = resolution
        self.picam.preview_configuration.main.size = resolution
        self.picam.preview_configuration.main.format = "RGB888"
        self.picam.configure("preview")
        self.picam.start()
        time.sleep(1)  # Camera warm-up

    def get_frame(self):
        frame = self.picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV
        return frame

    def stop(self):
        self.picam.close()


def main():
    print("[INFO] Initializing face detector...")
    detector = HailoFaceDetector(str(HEF_PATH))

    print("[INFO] Starting camera feed...")
    cam = CameraInterface()

    try:
        while True:
            frame = cam.get_frame()
            detections = detector.detect_faces(frame)
            print(f"[DEBUG] Detections: {detections}")
            print(f"[DEBUG] Frame shape: {frame.shape}")

            for x, y, w, h, score in detections:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{score:.2f}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

            cv2.imshow("Live Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        print("[INFO] Shutting down...")
        cam.stop()
        cv2.destroyAllWindows()
        detector.close()


if __name__ == "__main__":
    main()
