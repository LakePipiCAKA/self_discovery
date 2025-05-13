def create_new_user(name, camera=None, snapshot_count=3):
    """Creates a new user profile with multiple snapshots and facial embeddings."""
    import face_recognition
    from datetime import datetime
    from PyQt5.QtWidgets import QApplication

    user_id = name.lower().replace(" ", "_")
    user_folder = os.path.join(USER_DATA_ROOT, user_id)
    os.makedirs(user_folder, exist_ok=True)

    profile = DEFAULT_PROFILE_TEMPLATE.copy()
    profile["name"] = name
    profile["registered"] = True

    embeddings = []
    training_images = []

    for i in range(snapshot_count):
        # Prompt before capturing
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(f"Snapshot {i+1}/{snapshot_count}")
        msg.setText("Please center your face and press OK to capture.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        time.sleep(1.5)  # Let user reposition
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
            embeddings.append(encodings[0].tolist())  # Ensure it's JSON serializable
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

    save_profile(user_id, profile)
    print(f"🎉 Registered '{name}' with {len(embeddings)} snapshot(s).")
