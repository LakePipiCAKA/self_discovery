
# /home/taran/self_discovery/gui/main_app_launch.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import numpy as np
import requests
import time
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Import the reusable Hailo face detector module
from face_detection.hailo_face_detector import HailoFaceDetector

class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("Smart Mirror")
        self.setGeometry(100, 100, 800, 600)

        # Layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.info_label = QLabel("Loading time and weather...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        # Camera initialization
        from camera.camera_interface import CameraInterface
        self.camera = CameraInterface()

        # Hailo model path
        hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
        try:
            self.face_detector = HailoFaceDetector(hef_path)
        except Exception as e:
            print(f"❌ Failed to initialize HailoFaceDetector: {e}")
            self.face_detector = None

        # Timers for GUI updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time_weather)
        self.clock_timer.start(60000)

        self.update_time_weather()

    def update_time_weather(self):
        current_time = time.strftime("%H:%M:%S")
        weather = self.get_weather()
        self.info_label.setText(f"Time: {current_time} | Weather: {weather}")

    def get_weather(self):
        try:
            lat, lon = 45.6528, 25.6108  # Brasov
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(url)
            temperature = response.json()["current_weather"]["temperature"]
            return f"{temperature}°C"
        except Exception as e:
            print(f"⚠️ Weather fetch error: {e}")
            return "N/A"

    def update_frame(self):
        if not self.face_detector:
            return

        frame = self.camera.get_frame()
        if frame is None:
            return

        frame = cv2.flip(frame, 1)

        try:
            boxes = self.face_detector.detect_faces(frame)
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return

        print(f"📸 Detected {len(boxes)} face(s)")

        # Draw bounding boxes with confidence
        for detection in boxes:
            if len(detection) >= 5:
                x, y, w, h, conf = detection[:5]
                label = f"{conf:.2f}"
            else:
                x, y, w, h = detection
                label = "Face"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image.scaled(800, 500, Qt.KeepAspectRatio)))

    def closeEvent(self, event):
        if self.camera:
            self.camera.stop()
        if self.face_detector:
            self.face_detector.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartMirrorApp()
    window.show()
    sys.exit(app.exec_())
