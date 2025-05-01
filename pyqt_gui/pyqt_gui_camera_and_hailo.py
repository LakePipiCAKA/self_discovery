# pyqt_gui/pyqt_gui_camera_and_hailo.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
from src.camera.camera_interface import CameraInterface
from src.face_detection.hailo_face_detector import HailoFaceDetector


class MainWindow(QWidget):  # Make sure this line is present!
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Mirror")
        self.setStyleSheet("background-color: black;")

        # Create layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # Time label
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("color: white; font-size: 60px;")
        self.time_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Weather label
        self.weather_label = QLabel("70°F\nWind: 5 mph")
        self.weather_label.setStyleSheet("color: lightgray; font-size: 30px;")
        self.weather_label.setAlignment(Qt.AlignTop | Qt.AlignRight)

        # Location label
        self.location_label = QLabel("Chandler, AZ")
        self.location_label.setStyleSheet("color: gray; font-size: 24px;")
        self.location_label.setAlignment(Qt.AlignCenter)

        # Camera status label
        self.camera_status_label = QLabel("Camera: Initializing...")
        self.camera_status_label.setStyleSheet("color: yellow; font-size: 14px;")
        self.camera_status_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        # Face detection status label
        self.face_status_label = QLabel("Face Detection: Initializing...")
        self.face_status_label.setStyleSheet("color: yellow; font-size: 14px;")
        self.face_status_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        # Exit instruction label
        self.exit_label = QLabel("Press ESC or Q to exit")
        self.exit_label.setStyleSheet("color: darkgray; font-size: 12px;")
        self.exit_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        # Add widgets to layouts
        top_layout.addWidget(self.time_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self.weather_label)

        bottom_layout.addWidget(self.camera_status_label)
        bottom_layout.addWidget(self.face_status_label)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.exit_label)

        main_layout.addLayout(top_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(self.location_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        # Set up timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Initialize camera
        self.camera = CameraInterface()
        if self.camera.initialize():
            self.camera_status_label.setText("Camera: Ready")
            self.camera_status_label.setStyleSheet("color: green; font-size: 14px;")

            # Initialize face detector
            self.face_detector = HailoFaceDetector()
            self.face_status_label.setText("Face Detection: Ready")
            self.face_status_label.setStyleSheet("color: green; font-size: 14px;")

            # Add a timer to capture and process frames
            self.camera_timer = QTimer(self)
            self.camera_timer.timeout.connect(self.process_camera_frame)
            self.camera_timer.start(500)  # Process every 500ms
        else:
            self.camera_status_label.setText("Camera: Failed")
            self.camera_status_label.setStyleSheet("color: red; font-size: 14px;")

        # Initial time update
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

    def update_weather(self, temperature, wind):
        self.weather_label.setText(f"{temperature}°F\nWind: {wind} mph")

    def process_camera_frame(self):
        frame = self.camera.capture_frame()
        if frame is not None:
            # Run face detection
            faces = self.face_detector.detect_faces(frame)

            if len(faces) > 0:
                self.face_status_label.setText(
                    f"Face Detection: {len(faces)} face(s) detected"
                )
                self.face_status_label.setStyleSheet("color: green; font-size: 14px;")
            else:
                self.face_status_label.setText("Face Detection: No faces")
                self.face_status_label.setStyleSheet("color: blue; font-size: 14px;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.close()

    def closeEvent(self, event):
        """Handle cleanup when closing"""
        if hasattr(self, 'camera'):
            self.camera.cleanup()
        if hasattr(self, 'face_detector'):
            self.face_detector.cleanup()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # or window.showFullScreen()
    sys.exit(app.exec_())