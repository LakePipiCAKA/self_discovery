# pyqt_gui/Main_App_Launch.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..','src'))

import cv2
import numpy as np
import requests
import time
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Import your new face detector
from face_detection.hailo_face_detector import HailoFaceDetector

class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Basic window settings
        self.setWindowTitle("Smart Mirror")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Time and weather label
        self.info_label = QLabel("Loading time and weather...", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # Camera feed label
        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label)

        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Default camera (Pi Camera or USB Cam)

        # Initialize Hailo Face Detector
        hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"  # Update if needed
        self.face_detector = HailoFaceDetector(hef_path)

        # Set up timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time_weather)
        self.clock_timer.start(60000)  # Update every 60 seconds

        self.update_time_weather()  # Initial weather fetch

    def update_time_weather(self):
        # Get current time
        current_time = time.strftime("%H:%M:%S")

        # Fetch weather
        weather = self.get_weather()

        # Update label
        self.info_label.setText(f"Time: {current_time} | Weather: {weather}")

    def get_weather(self):
        try:
            latitude = 45.6528  # Brasov, Romania
            longitude = 25.6108
            response = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
            )
            data = response.json()
            temperature = data["current_weather"]["temperature"]
            return f"{temperature}°C"
        except Exception as e:
            print(f"Weather fetch error: {e}")
            return "N/A"

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Mirror effect

            # Face detection
            boxes = self.face_detector.detect_faces(frame)

            # Draw rectangles around faces
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convert frame to display
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = qt_image.scaled(800, 500, Qt.KeepAspectRatio)

            self.camera_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        # Release resources cleanly
        self.cap.release()
        self.face_detector.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartMirrorApp()
    window.show()
    sys.exit(app.exec_())
