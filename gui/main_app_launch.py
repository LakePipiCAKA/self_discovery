# /home/taran/self_discovery/gui/main_app_launch.py (updated with GUI-integrated registration flow)

import sys
import os
import cv2
import numpy as np
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QDateEdit,
    QComboBox,
)
from PyQt5.QtCore import QTimer, Qt, QDate
from PyQt5.QtGui import QImage, QPixmap, QFont

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from camera.camera_interface import CameraInterface
from face_detection.face_detector import HailoFaceDetector
from user_management.user_profiles import (
    ProfileDetailsDialog,
    save_profile,
    load_profiles,
    DEFAULT_PROFILE_TEMPLATE,
)

from weather.open_meteo import get_weather


class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Mirror")
        self.setGeometry(100, 100, 800, 600)

        # Layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.info_label = QLabel("Time & Weather loading...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.greeting_label = QLabel("❤️ Hello there beautiful stranger!")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setFont(QFont("Arial", 16))
        self.layout.addWidget(self.greeting_label)

        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        self.setup_btn = QPushButton("My Mirror Set Up")
        self.setup_btn.clicked.connect(self.begin_registration_sequence)
        self.layout.addWidget(self.setup_btn)

        self.camera = CameraInterface()
        self.face_detector = HailoFaceDetector(
            "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
        )
        self.users = load_profiles()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(60000)

        self.update_time("Europe/Bucharest")
        self.in_registration = False
        self.capture_count = 0
        self.registration_data = {}

    def update_time(self, timezone=None):
        import pytz
        from datetime import datetime

        # Use active user if available
        user_profile = getattr(self, "active_user", None)

        # Timezone logic
        if timezone is None:
            if (
                user_profile
                and user_profile.get("location", {}).get("country", "").lower()
                == "romania"
            ):
                timezone = "Europe/Bucharest"
            elif not user_profile:
                timezone = "Europe/Bucharest"  # Default
            else:
                timezone = "UTC"

        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%H:%M:%S")

        # Weather logic
        weather = get_weather(user_profile["location"] if user_profile else "default")
        weather_text = f"{weather['location']}: {weather['temperature']}°F • {weather['condition']} • Wind {weather['wind']} mph"

        self.info_label.setText(f"Time: {now} | {weather_text}")

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is None:
            return

        frame = cv2.flip(frame, 1)

        if self.in_registration:
            overlay = f"Capturing in {3 - self.capture_count}…"
            self.greeting_label.setText(overlay)

            if self.capture_count < 3:
                if (
                    not hasattr(self, "last_capture_time")
                    or time.time() - self.last_capture_time > 2
                ):
                    self.capture_snapshot(frame)
                    self.capture_count += 1
                    self.last_capture_time = time.time()
                else:
                    pass  # wait
            else:
                self.finish_registration()
                return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.camera_label.setPixmap(
            QPixmap.fromImage(qt_img).scaled(800, 500, Qt.KeepAspectRatio)
        )

    def begin_registration_sequence(self):
        from user_management.user_profiles import ProfileDetailsDialog

        dialog = ProfileDetailsDialog()
        if not dialog.exec_():
            print("🚫 User canceled registration.")
            return

        name = dialog.get_name()

        location = dialog.get_location()

        if not location.get("city") or not location.get("country"):
            print("❗ City and Country are required. Registration canceled.")
            return

        self.registration_data = {
            "name": name,
            "location": location,
            "dob": dialog.get_dob(),
            "sex": dialog.get_sex(),
            "snapshots": [],
            "encodings": [],
        }
        self.in_registration = True
        self.capture_count = 0
        print("🟢 Starting registration in GUI mode")
        print("🟢 Starting registration in GUI mode")

    def capture_snapshot(self, frame):
        import face_recognition

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        user_id = self.registration_data["name"].lower()
        folder = os.path.join("data", "users", user_id)
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"{timestamp}_snap{self.capture_count+1}.jpg")
        cv2.imwrite(filename, frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if encs:
            self.registration_data["encodings"].append(encs[0].tolist())
            self.registration_data["snapshots"].append(filename)
            print(f"✅ Captured and saved {filename}")
        else:
            print("⚠️ No face detected in snapshot")

    def finish_registration(self):
        profile = DEFAULT_PROFILE_TEMPLATE.copy()
        profile["name"] = self.registration_data["name"]
        profile["registered"] = True
        profile["location"].update(self.registration_data["location"])
        profile["date_of_birth"] = self.registration_data["dob"]
        profile["sex"] = self.registration_data["sex"]
        profile["facial_data"]["encodings"] = self.registration_data["encodings"]
        profile["facial_data"]["training_images"] = self.registration_data["snapshots"]
        profile["snapshots"] = self.registration_data["snapshots"]

        user_id = self.registration_data["name"].lower()
        save_profile(user_id, profile)
        self.users = load_profiles()  # Refresh user profiles
        self.active_user = profile  # 🔄 Set active user for location/time
        self.update_time()
        self.greeting_label.setText(f"🎉 Welcome, {profile['name']}!")
        print("✔️ Registration completed")
        self.in_registration = False

    def closeEvent(self, event):
        self.camera.stop()
        self.face_detector.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply global dark stylesheet
    app.setStyleSheet(
        """
    QWidget {
        background-color: #121212;
        color: #FFFFFF;
    }
    QLabel {
        font-size: 14px;
    }
    QPushButton {
        font-size: 14px;
        padding: 6px 12px;
        border-radius: 8px;
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    QPushButton:hover {
        background-color: #3D3D3D;
    }
"""
    )
    window = SmartMirrorApp()
    window.show()
    sys.exit(app.exec_())
