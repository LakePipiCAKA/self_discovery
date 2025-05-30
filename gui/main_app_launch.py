# /home/taran/self_discovery/gui/main_app_launch.py

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
)
from PyQt5.QtCore import QTimer, Qt
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
import face_recognition
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz


class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Mirror")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.info_label = QLabel("Time & Weather loading...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.greeting_label = QLabel("❤️ Hello there stranger!")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setFont(QFont("Arial", 16))
        self.layout.addWidget(self.greeting_label)

        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        self.setup_btn = QPushButton("+ Add New User")
        self.setup_btn.clicked.connect(self.begin_registration_sequence)
        self.layout.addWidget(self.setup_btn)

        self.switch_btn = QPushButton("Switch User")
        self.switch_btn.clicked.connect(self.reset_recognition)
        self.layout.addWidget(self.switch_btn)

        self.camera = CameraInterface()
        self.face_detector = HailoFaceDetector("/usr/share/hailo-models/yolov5s_personface_h8l.hef")
        self.users = load_profiles()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(60000)

        self.update_time("Europe/Bucharest")
        self.in_registration = False
        self.capture_count = 0
        self.registration_data = {}
        self.frame_count = 0
        self.recognition_active = True
        self.snapshot_log = set()
        self.active_user = None
        self.registration_prompts = ["Look straight ahead", "Look left", "Look right", "Smile"]

        if self.active_user:
            self.setup_btn.hide()

    def update_time(self, timezone=None):
        user_profile = getattr(self, "active_user", None)
        if timezone is None:
            if user_profile:
                loc = user_profile.get("location", {})
                location_str = f"{loc.get('city', '')}, {loc.get('state', '')}, {loc.get('country', '')}"
                try:
                    geolocator = Nominatim(user_agent="smart_mirror")
                    location = geolocator.geocode(location_str)
                    if location:
                        tf = TimezoneFinder()
                        timezone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
                    else:
                        timezone = "UTC"
                except:
                    timezone = "UTC"
            else:
                timezone = "Europe/Bucharest"

        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%H:%M:%S")

        weather = get_weather(user_profile.get("location", {}) if user_profile else "default")
        weather_text = f"{weather['location']}: {weather['temperature']}°F • {weather['condition']} • Wind {weather['wind']} mph"

        self.info_label.setText(f"Time: {now} | {weather_text}")

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is None:
            return

        frame = cv2.flip(frame, 1)

        if self.in_registration:
            prompt = self.registration_prompts[self.capture_count] if self.capture_count < len(self.registration_prompts) else ""
            self.greeting_label.setText(f"{prompt} ({self.capture_count + 1}/4)")

            if self.capture_count < len(self.registration_prompts):
                if not hasattr(self, "last_capture_time") or time.time() - self.last_capture_time > 2:
                    self.capture_snapshot(frame)
                    self.capture_count += 1
                    self.last_capture_time = time.time()
                return
            else:
                self.finish_registration()
                return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small_rgb = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
        self.frame_count += 1

        if self.recognition_active and self.frame_count % 15 == 0:
            face_locations = face_recognition.face_locations(small_rgb)
            face_encodings = face_recognition.face_encodings(small_rgb, face_locations)

            for face_encoding in face_encodings:
                best_match = None
                best_distance = float("inf")
                for user_id, profile in self.users.items():
                    known_encs = profile.get("facial_data", {}).get("encodings", [])
                    known_encs_np = np.array(known_encs)
                    if not known_encs_np.any():
                        continue
                    distances = face_recognition.face_distance(known_encs_np, face_encoding)
                    min_dist = np.min(distances)
                    if min_dist < 0.45 and min_dist < best_distance:
                        best_match = profile
                        best_distance = min_dist

                if best_match:
                    self.active_user = best_match
                    self.setup_btn.hide()
                    self.update_time()
                    self.greeting_label.setText(f"🌞 Welcome back, {best_match['name']}!")
                    print(f"✅ Recognized user: {best_match['name']} (distance: {best_distance:.2f})")
                    self.recognition_active = False
                    self.capture_daily_snapshot(frame)
                    break
                else:
                    self.greeting_label.setText("😕 I don't recognize you yet. Want to add a profile?")

        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img).scaled(800, 500, Qt.KeepAspectRatio))

    def begin_registration_sequence(self):
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

    def capture_snapshot(self, frame):
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
        encs = np.array(self.registration_data["encodings"])
        mean_vec = np.mean(encs, axis=0)
        dists = np.linalg.norm(encs - mean_vec, axis=1)
        filtered_encs = encs[dists < 0.5]

        profile.update({
            "name": self.registration_data["name"],
            "registered": True,
            "location": self.registration_data["location"],
            "date_of_birth": self.registration_data["dob"],
            "sex": self.registration_data["sex"],
            "facial_data": {
                "encodings": filtered_encs.tolist(),
                "training_images": self.registration_data["snapshots"]
            },
            "snapshots": self.registration_data["snapshots"]
        })

        user_id = profile["name"].lower()
        save_profile(user_id, profile)
        self.users = load_profiles()
        self.active_user = profile
        self.update_time()
        self.greeting_label.setText(f"🎉 Welcome, {profile['name']}!")
        print("✔️ Registration completed")
        self.in_registration = False

    def reset_recognition(self):
        self.active_user = None
        self.recognition_active = True
        self.greeting_label.setText("🔄 Please look at the mirror for recognition")
        self.setup_btn.show()

    def capture_daily_snapshot(self, frame):
        if not self.active_user:
            return

        now = datetime.now()
        hour = now.hour
        period = (
            "morning" if 5 <= hour < 12 else
            "afternoon" if 12 <= hour < 17 else
            "evening" if 17 <= hour < 21 else None
        )
        if not period:
            return

        date_key = f"{self.active_user['name']}_{now.date()}_{period}"
        if date_key in self.snapshot_log:
            return  # already captured

        user_id = self.active_user["name"].lower()
        folder = os.path.join("data", "users", user_id)
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"{now.strftime('%Y-%m-%d_%H%M%S')}_{period}.jpg")
        cv2.imwrite(filename, frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if encs:
            enc = encs[0].tolist()
            profile = self.active_user
            profile["facial_data"].setdefault("encodings", []).append(enc)
            if len(profile["facial_data"]["encodings"]) > 10:
                profile["facial_data"]["encodings"] = profile["facial_data"]["encodings"][-10:]
            profile.setdefault("snapshots", []).append(filename)
            save_profile(user_id, profile)
            print(f"📸 Daily snapshot captured: {filename}")

        self.snapshot_log.add(date_key)

        # Save placeholder daily tip
        tips_path = os.path.join(folder, "daily_tips.json")
        import json
        try:
            with open(tips_path, "r") as f:
                tips_data = json.load(f)
        except FileNotFoundError:
            tips_data = {}

        tips_data[f"{now.date()}_{period}"] = "💡 (pending update)"
        with open(tips_path, "w") as f:
            json.dump(tips_data, f, indent=2)

        print(f"📝 Saved daily tip placeholder for {now.date()} {period} time")


    def closeEvent(self, event):
        self.camera.stop()
        self.face_detector.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    def load_stylesheet(path):
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ QSS file not found: {path}")
            return ""

    qss = load_stylesheet("gui/themes/dark_theme.qss")
    app.setStyleSheet(qss)
    window = SmartMirrorApp()
    window.show()
    sys.exit(app.exec_())
