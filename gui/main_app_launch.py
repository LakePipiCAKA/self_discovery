import sys
import os
import cv2
import numpy as np
import requests
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from face_detection.face_detector import HailoFaceDetector
from camera.camera_interface import CameraInterface
from user_management.user_profiles import load_profiles, save_profile, create_new_user


class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Mirror")
        self.setGeometry(100, 100, 800, 600)

        # Layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.info_label = QLabel("Loading time and weather...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.greeting_label = QLabel("😴 Waiting for face...")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.greeting_label)

        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        self.camera = CameraInterface()
        hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"

        try:
            self.face_detector = HailoFaceDetector(hef_path)
        except Exception as e:
            print(f"❌ Failed to initialize HailoFaceDetector: {e}")
            self.face_detector = None

        self.users = load_profiles()
        if not self.users:
            print("⚠️ No registered users. Running in limited mode.")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time_weather)
        self.clock_timer.start(60000)

        self.update_time_weather()
        self.blur_when_no_face = True

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

        face_found = len(boxes) > 0
        self.greeting_label.setText(
            "👋 Hello there!" if face_found else "😴 Waiting for face..."
        )

        if not face_found and self.blur_when_no_face:
            frame = cv2.GaussianBlur(frame, (15, 15), 0)

        for detection in boxes:
            if len(detection) >= 5:
                x, y, w, h, conf = detection[:5]
                label = f"{conf:.2f}"
            else:
                x, y, w, h = detection
                label = "Face"

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.camera_label.setPixmap(
            QPixmap.fromImage(qt_image.scaled(800, 500, Qt.KeepAspectRatio))
        )

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
