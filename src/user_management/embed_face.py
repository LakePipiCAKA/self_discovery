import os
import face_recognition
import json

USER_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")
USER_DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/users")
)


def load_profiles():
    if not os.path.exists(USER_PROFILE_PATH):
        return {}
    with open(USER_PROFILE_PATH, "r") as f:
        return json.load(f)


def save_profiles(profiles):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)


def generate_embedding(user_id):
    profiles = load_profiles()

    if user_id not in profiles:
        print(f"❌ No profile found for user ID '{user_id}'.")
        return False

    user_folder = os.path.join(USER_DATA_ROOT, user_id)
    snapshot_path = os.path.join(user_folder, "snapshot.jpg")

    if not os.path.exists(snapshot_path):
        print(f"❌ No snapshot found at {snapshot_path}")
        return False

    image = face_recognition.load_image_file(snapshot_path)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        print("⚠️ No face detected in snapshot.")
        return False

    face_encodings = face_recognition.face_encodings(
        image, known_face_locations=face_locations
    )
    if not face_encodings:
        print("⚠️ Failed to compute face encoding.")
        return False

    # Use first face only
    embedding = face_encodings[0]
    profiles[user_id]["facial_data"]["encodings"] = embedding.tolist()

    save_profiles(profiles)
    print(f"✅ Embedding generated and saved for '{user_id}'.")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python embed_face.py <user_id>")
    else:
        user_id = sys.argv[1]
        generate_embedding(user_id)
