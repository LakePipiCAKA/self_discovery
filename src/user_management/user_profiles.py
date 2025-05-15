import os
import cv2
import json
import time
import face_recognition
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import QDate

USER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")
USER_DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/users")
)

DEFAULT_PROFILE_TEMPLATE = {
    "name": "",
    "registered": False,
    "location": {"city": "", "state": "", "country": "", "lat": 0.0, "lon": 0.0},
    "date_of_birth": None,
    "sex": None,
    "preferences": {"display_tips": True},
    "facial_data": {"encodings": [], "training_images": []},
    "snapshots": [],
}


from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont


class ProfileDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Complete Your Profile")
        self.setStyleSheet(
            """
            QDialog {
                background-color: #121212;
                color: #FFFFFF;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QComboBox {
                font-size: 14px;
                padding: 6px;
                border-radius: 8px;
                border: 1px solid #555;
                background-color: #1E1E1E;
                color: #FFFFFF;
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
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        name_label = QLabel("👤 Name (required):")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        self.name_input.setPlaceholderText("Enter your full name")

        self.city_input = QLineEdit()
        city_label = QLabel("📍 City (required):")
        layout.addWidget(city_label)
        layout.addWidget(self.city_input)

        self.state_input = QLineEdit()
        state_label = QLabel("🏛 State (optional):")
        layout.addWidget(state_label)
        layout.addWidget(self.state_input)

        self.country_input = QLineEdit()
        country_label = QLabel("🌍 Country (required):")
        layout.addWidget(country_label)
        layout.addWidget(self.country_input)

        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("MM/dd/yyyy")
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate().addYears(-25))
        dob_label = QLabel("🎂 Date of Birth:")
        layout.addWidget(dob_label)
        layout.addWidget(self.dob_input)

        self.sex_dropdown = QComboBox()
        self.sex_dropdown.addItems(["Male", "Female", "Other", "Prefer not to say"])
        sex_label = QLabel("👤 Sex:")
        layout.addWidget(sex_label)
        layout.addWidget(self.sex_dropdown)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Center the dialog
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen)
        self.move(frame_geometry.topLeft())

    def get_location(self):
        return {
            "city": self.city_input.text(),
            "state": self.state_input.text(),
            "country": self.country_input.text(),
        }

    def get_dob(self):
        return self.dob_input.date().toString("MM/dd/yyyy")

    def get_sex(self):
        return self.sex_dropdown.currentText()

    def get_name(self):
        return self.name_input.text()


def create_new_user(name, camera=None, snapshot_count=3):
    user_id = name.lower().replace(" ", "_")
    user_folder = os.path.join(USER_DATA_ROOT, user_id)
    os.makedirs(user_folder, exist_ok=True)

    profile = DEFAULT_PROFILE_TEMPLATE.copy()
    profile["name"] = name
    profile["registered"] = True

    dialog = ProfileDetailsDialog()
    if not dialog.exec_():
        print("🚫 User canceled registration.")
        return

    location = dialog.get_location()
    if not location["city"] or not location["country"]:
        print("❗ City and Country are required. User not saved.")
        return

    profile["location"].update(location)
    profile["date_of_birth"] = dialog.get_dob()
    profile["sex"] = dialog.get_sex()

    embeddings = []
    training_images = []

    for i in range(snapshot_count):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(f"Snapshot {i+1}/{snapshot_count}")
        msg.setText("Please center your face and press OK to capture.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        time.sleep(1.5)
        if not camera:
            print("⚠️ No camera provided.")
            continue

        frame = camera.get_frame()
        if frame is None:
            print("⚠️ Frame not captured.")
            continue

        frame = cv2.flip(frame, 1)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{timestamp}_snap{i+1}.jpg"
        image_path = os.path.join(user_folder, filename)
        cv2.imwrite(image_path, frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if encodings:
            embeddings.append(encodings[0].tolist())
            training_images.append(image_path)
            print(f"✅ Saved: {image_path}")
        else:
            print(f"⚠️ No face found in snapshot {i+1}. Skipped.")

    if not embeddings:
        print("❌ No valid encodings. User not saved.")
        return

    profile["facial_data"]["encodings"] = embeddings
    profile["facial_data"]["training_images"] = training_images
    profile["snapshots"] = training_images.copy()

    save_profile(user_id, profile)
    print(f"🎉 Registered '{name}' with {len(embeddings)} snapshot(s).")


def load_profiles():
    if not os.path.exists(USER_PROFILE_PATH):
        return {}
    try:
        with open(USER_PROFILE_PATH, "r") as f:
            data = json.load(f)
            for user_id, profile in data.items():
                for key, default_value in DEFAULT_PROFILE_TEMPLATE.items():
                    if key not in profile:
                        profile[key] = default_value
            return data
    except json.JSONDecodeError:
        return {}


def save_profile(user_id, profile):
    profiles = load_profiles()
    profiles[user_id] = profile
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)
