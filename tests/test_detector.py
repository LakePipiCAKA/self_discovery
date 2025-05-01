import cv2
from src.face_detection.hailo_face_detector import HailoFaceDetector

# Load a test image
frame = cv2.imread("camera_test.jpg")  # Make sure this file exists

# Path to your model
hef_path = "models/hailo/yolov5s_personface_h8l.hef"

# Initialize detector
detector = HailoFaceDetector(hef_path)

# Run face detection
boxes = detector.detect_faces(frame)

# Show results
for (x, y, w, h) in boxes:
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Detections", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Cleanup
detector.close()
