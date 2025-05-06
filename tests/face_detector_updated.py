# /home/taran/self_discovery/tests/face_detector_updated.py
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from src.face_detection.hailo_face_detector import HailoFaceDetector

class SmartMirrorCamera:
    def __init__(self, resolution=(640, 480)):
        # Initialize camera
        self.picam = Picamera2()
        self.resolution = resolution
        self.picam.preview_configuration.main.size = resolution
        self.picam.preview_configuration.main.format = "RGB888"
        self.picam.configure("preview")
        self.picam.start()
        time.sleep(1)  # Let camera warm up
        
        # Initialize face detector
        self._setup_face_detector()
        
    def _setup_face_detector(self):
        """Set up the Hailo face detector"""
        try:
            hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
            self.face_detector = HailoFaceDetector(hef_path)
            self.face_detector_ready = True
            print("Face detector ready")
        except Exception as e:
            print(f"Failed to initialize face detector: {e}")
            import traceback
            traceback.print_exc()
            self.face_detector_ready = False
            # Use placeholder detection instead
            self.use_placeholder = True
            print("Using placeholder detection instead")
    
    def detect_faces_placeholder(self, frame):
        """Placeholder face detection when Hailo is not available"""
        h, w = frame.shape[:2]
        center_x = w // 2
        center_y = h // 2
        face_w = w // 4
        face_h = h // 4
        
        return [(center_x - face_w//2, center_y - face_h//2, face_w, face_h, 0.95)]
    
    def get_frame(self, detect_faces=False, rgb=False):
        """Get a frame from the camera, optionally with face detection"""
        frame = self.picam.capture_array()
        
        if rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        if detect_faces:
            if self.face_detector_ready:
                try:
                    # Use Hailo face detector
                    faces = self.face_detector.detect_faces(frame)
                    print(f"Detected {len(faces)} faces")
                except Exception as e:
                    print(f"Face detection error: {e}")
                    # Fall back to placeholder
                    faces = self.detect_faces_placeholder(frame)
            else:
                # Use placeholder detection
                faces = self.detect_faces_placeholder(frame)
            
            # Draw bounding boxes
            for face in faces:
                x, y, w, h, conf = face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{conf:.2f}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame

    def stop(self):
        """Close camera and cleanup resources"""
        self.picam.close()
        if hasattr(self, 'face_detector') and self.face_detector_ready:
            self.face_detector.close()

# Test mode
if __name__ == "__main__":
    cam = SmartMirrorCamera()
    try:
        while True:
            frame = cam.get_frame(detect_faces=True)
            cv2.imshow("Smart Mirror Camera Feed with Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.stop()
        cv2.destroyAllWindows()