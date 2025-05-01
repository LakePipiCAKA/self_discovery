# /home/taran/smart_mirror_project/src/face_detection/test_face_detector.py
import cv2
from hailo_face_detector import HailoFaceDetector

def main():
    detector = HailoFaceDetector()
    cap = cv2.VideoCapture(0)  # Adjust index if needed
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            faces = detector.detect_faces(frame)
            for face in faces:
                x_min, y_min, x_max, y_max = face['bbox']
                conf = face['confidence']
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(
                    frame, f"Conf: {conf:.2f}", (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
            
            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.cleanup()

if __name__ == "__main__":
    main()