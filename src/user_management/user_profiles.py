import json
import os
import cv2

USER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")
USER_DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/users")
)

DEFAULT_PROFILE_TEMPLATE = {
    "name": "",
    "registered": False,
    "location": {"name": "Unknown", "country": "Unknown", "lat": 0.0, "lon": 0.0},
    "date_of_birth": None,
    "sex": None,
    "preferences": {"display_tips": True},
    "facial_data": {"encodings": [], "training_images": []},
    "snapshots": [],
}


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


def create_new_user(name, camera=None):
    """Creates a new user profile, saves it, and captures one face snapshot if camera is provided."""
    user_id = name.lower().replace(" ", "_")
    user_folder = os.path.join(USER_DATA_ROOT, user_id)
    os.makedirs(user_folder, exist_ok=True)

    profile = DEFAULT_PROFILE_TEMPLATE.copy()
    profile["name"] = name
    profile["registered"] = True

    snapshot_path = os.path.join(user_folder, "snapshot.jpg")

    if camera:
        frame = camera.get_frame()
        if frame is not None:
            frame = cv2.flip(frame, 1)
            cv2.imwrite(snapshot_path, frame)
            print(f"📸 Saved snapshot for {name} at {snapshot_path}")
            profile["snapshots"].append(snapshot_path)
        else:
            print("⚠️ Camera frame not captured.")
    else:
        print("⚠️ No camera provided — skipping snapshot.")

    save_profile(user_id, profile)
