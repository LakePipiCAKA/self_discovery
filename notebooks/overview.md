## 🧑‍🎨 General Use Case & Flow

When the Smart Mirror powers on (either via actual mirror hardware or a touchscreen device), it launches the main app.
<!-- confirmed working as of 2025-05-06 -->

### 👋 Default (Non-Identified User)
- Displays greeting: **"Hello there beautiful!"** at the top.
- The **center of the screen remains clear**, acting as a traditional mirror.
- Users can:
  - Use the mirror in "no profile" mode
  - Or choose to **Create Profile**
- In "no profile" mode, the mirror displays:
  - Time
  - Weather (user types in City, Country)

---

### 🧑‍💼 Profile Creation Flow
- Prompts the user for:
  - Name
  - Location
  - Date of birth
  - Sex
- Includes **face training and image capture** to recognize the user later.
- Profile data and face encoding are saved locally (TBD storage strategy).
![Basic Wire Frame](image.png)

---

### 🗂️ User Profile Management
- Profiles are stored in a lightweight JSON (`src/user_management/user_profiles.json`)
- Users are currently limited to 4–5
- Each profile contains:
  - Name, Location (lat/lon), City
  - Date of birth
  - Sex
  - [Future] Skin analysis metrics or reference history
<!-- confirmed updated JSON format 2025-05-06 -->

---

### 🧠 Face Detection and Recognition
- Powered by **Hailo-8L** accelerator and `.hef` model:
  - `models/hailo/yolov5s_personface_h8l.hef`
  - Uses `yolov5_nms_postprocess` as output key
- Bounding boxes now confirmed working via `face_detector.py` <!--May need tweaking, square not around the face, bounce around 5/6/25->
<!-- Confirmed 2025-05-06. Not using Haarcascade. -->

---

### 📁 Folder Structure (as of 2025-05-06)

self_discovery/
├── data/users # [future] user image or health tracking data
├── gui/main_app_launch.py # Launches PyQt GUI, calls face detector <!--Woking 5/6/25-->
├── models/hailo/ # Hailo model + config <!--WORKING 5/6/25-->
│ ├── yolov5_personface.json
│ └── yolov5s_personface_h8l.hef
├── notebooks/
│ ├── `overview.md` # This file
│ ├── devlog.md # Running log of changes
│ └── `image.png` # Sample wireframe
├── src/
│ ├── camera/ # camera_interface.py for libcamera access
│ ├── face_detection/ # `face_detector.py' <!--working 5/6/25
│ ├── ui/ # Stubbed PyQt UI handlers
│ ├── user_analysis/ # Placeholder for future skin/health trends
│ ├── user_management/ # JSON profiles, new user creation
│ └── weather/ # Weather logic using Open-Meteo API
├── tests/ # Includes camera + model test scripts
└── requirements.txt # Installed in venv

<!-- Scripts like hailo_face_detector_flat_display.py deprecated — no longer referenced in GUI -->

---

### 📊 Future Plans (Post MVP)
- Add profile settings screen (PyQt)
- Health tracking via face analysis (skin, weight, alerting changes)
- More flexible location input (no GPS, this is a mirror proejct, select city/state/country)
- Create fallback if Hailo hardware not detected
- Profile deletion or editing via GUI
- Profile image preview
- Profile-specific settings (theme, layout, tips frequency)

---

### 🛠 Implementation Notes
- Camera handled through `camera_interface.py`
- GUI uses PyQt5, launches cleanly after reinstalling Qt plugins
- All inference offloaded to Hailo hardware
- Current JSON is sufficient; SQLite not needed for <10 users
