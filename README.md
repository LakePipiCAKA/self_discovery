# Smart Mirror Project

This project is a Python-based smart mirror interface using Raspberry Pi 5 and Hailo-8L AI accelerator. It integrates facial recognition, camera feeds, weather data, and user profile management with support for real-time AI inference using Hailo hardware.

---

## 💡 Key Features

- Touchscreen or mirrored display UI
- Dynamic greeting system for unidentified and recognized users
- Daily facial snapshots and visual logs
- Weather display based on profile or manual input
- Face detection using Hailo-8L with YOLOv5s (person/face model)
- Custom user profiles with face training and preferences
- Optional beauty tips feature (future scope)

---

## 📁 Project Structure

```bash
~/self_discovery
├── gui/
│   └── Main_App_Launch.py
├── models/
│   └── hailo/
│       └── yolov5s_personface_h8l.hef  (symlinked to /usr/share/hailo-models/)
├── notebooks/
│   ├── devlog.md
│   ├── overview.md
│   └── setup.ipynb
├── requirements.txt
├── README.md
├── src/
│   ├── camera/
│   │   └── camera_interface.py
│   ├── face_detection/
│   │   ├── hailo_face_detector.py
│   │   ├── test_face_detector.py
│   │   └── test_hailo.py
│   ├── ui/
│   │   ├── default.py
│   │   ├── monitoring_display.py
│   │   ├── recognition.py
│   │   ├── selection.py
│   │   └── training.py
│   ├── user_management/
│   │   ├── user_profiles.json
│   │   └── user_profiles.py
│   └── weather/
│       └── open_meteo.py
└── tests/
    ├── import_hailo_platform.py
    ├── test_basic_camera.py
    └── test_detector.py
```

---

## ⚙️ System Requirements

- **Hardware:** Raspberry Pi 5 (8GB) with Hailo-8L AI HAT
- **OS:** Debian GNU/Linux 12 (Bookworm), 64-bit aarch64
- **Python:** 3.11.2
- **Libraries:** Installed via `requirements.txt` + Hailo SDK v4.20.0

---

## 🚀 Getting Started

1. Clone the repository
2. Create virtual environment
3. Activate and install dependencies:
   ```bash
   python3 -m venv ~/smart_mirror_venv
   source ~/smart_mirror_venv/bin/activate
   pip install -r requirements.txt
   ```
4. Add symlink for model if needed:
   ```bash
   ln -s /usr/share/hailo-models/yolov5s_personface_h8l.hef ~/self_discovery/models/hailo/
   ```
5. Run:
   ```bash
   python src/camera/camera_interface.py
   ```

---

## 📌 Notes

- Camera tested using `Picamera2` with color correction (`RGB888`)
- Hailo model loading validated with `import_hailo_platform.py`
- `pyhailort` functionality depends on exact version match with Hailo driver 
