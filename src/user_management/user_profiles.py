import json
import os

USER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")

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
            # Ensure all required keys are present
            for user_id, profile in data.items():
                for key, default_value in DEFAULT_PROFILE_TEMPLATE.items():
                    if key not in profile:
                        profile[key] = default_value
            return data
    except json.JSONDecodeError:
        return {}


def create_new_user(name):
    """Creates a new user profile with default values."""
    return {
        "name": name,
        "location": {"name": "Unknown", "lat": 0.0, "lon": 0.0},
        "dob": None,
        "sex": None,
        "preferences": {"show_tips": True},
        "snapshots": [],
    }


def save_profile(user_id, profile):
    profiles = load_profiles()
    profiles[user_id] = profile
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)
