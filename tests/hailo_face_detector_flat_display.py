import sys
from pathlib import Path
import cv2

# Dynamically add project root (one level up from 'tests') to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.face_detection.face_detector import HailoFaceDetector



HEF_PATH = ROOT_DIR / "models/hailo/yolov5s_personface_h8l.hef"
IMAGE_PATH = ROOT_DIR / "tests/Smart Mirror Camera Feed_screenshot_04.05.2025.png"

def main():
    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise FileNotFoundError(f"Could not load image: {IMAGE_PATH}")
    
    detector = HailoFaceDetector(str(HEF_PATH))
    detections = detector.detect_faces(image)

    print(f"[INFO] Detections: {detections}")
    for (x, y, w, h, score, class_id) in detections:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, f"{score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("Detections", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
