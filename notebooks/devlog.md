# Smart Mirror Development Log

**Date:** 2025-05-03 16:35  
**Device:** Raspberry Pi 5 (8GB)  
**Accelerator:** Hailo-8L AI HAT (13 TOPS)  
**OS:** Debian GNU/Linux 12 (Bookworm)  
**Kernel:** 6.12.20 (64-bit aarch64)  
**Python:** 3.11.2  
**Virtual Environment:** `~/smart_mirror_venv`

---

## ✅ Project Goals Recap

- Touch-screen or mirror glass interface
- Greets unidentified users with "Hello there beautiful!"
- Time + weather overlay (city/country for no-profile users)
- Profile creation with face training (name, DOB, sex, location)
- User recognition and greeting
- Daily or periodic facial photos for visual health/beauty observations
- (Future) Tips based on visual changes

---

## 🧪 Hardware Validation

- ✅ Raspberry Pi 5 powers on cleanly
- ✅ Virtual environment `smart_mirror_venv` is active
- ✅ Picamera2 functional — live preview verified
- ✅ Camera image color corrected using `RGB888` format

---

## 🔧 Environment Setup Summary

- ✅ Jupyter and Markdown support in VS Code
- ✅ `tree` installed globally
- ✅ Venv interpreter configured in VS Code
- ✅ `opencv-python`, `numpy` installed in venv
- ✅ Picamera2 installed in system Python (used globally)
- ✅ HailoRT 4.20.0 installed (downgraded from 4.21 due to compatibility issues)
- ✅ `pyhailort` installed via `.whl` for Python 3.11 aarch64

---

## ⚠️ Hailo SDK Troubleshooting Summary

- Original install used `hailo-all` (v4.20.0) — confirmed functional
- Attempted 4.21 upgrade via `.deb` caused mismatch with driver (rolled back)
- Verified `/usr/share/hailo-models` contains models
- Created symlink in project: `models/hailo/yolov5s_personface_h8l.hef`
- Verified symbolic link is valid via `ls -l`
- `hailortcli fw-control identify` works (driver OK)
- `pyhailort` .whl installed but lacks higher-level bindings like `InferModel.input_streams`

---

## ❌ Current Blocker

Script `import_hailo_platform.py` attempts to use high-level `InferModel` helpers:
- `.input_streams`
- `.get_input_stream_infos()`
- `.configure().create_bindings()`

These methods do **not exist** in the current `pyhailort` version extracted from the `.whl`.

---

## 📌 Next Action Plan

### Option A — Recommended:
- Use reference structure from official working notebook:
  - `HRT_0_Async_Inference_Tutorial.ipynb`
- Rewrite the script using their lower-level API
- This avoids future mismatch or unsupported function calls

### Option B:
- Continue probing pyhailort’s internal structure using introspection
- Attempt a minimal dummy inference via `pyhailort` directly

---
## 🔁 Progress Update — 2025-05-04

### 🔍 Deeper Investigation into `pyhailort` from `.whl`
- Explored internal structure via introspection (`dir()` on modules)
- Found no `.create()` methods for `VDevice`
- Found `create_infer_model` on `VDevice`, followed by `.configure()`

### 🧪 Experimented Execution Path
- Initial constructor attempts failed with: `No constructor defined`
- Rewrote script using working pattern based on tutorial notebook and symbols found in `pyhailort._pyhailort`
- Example: `VDevice().create_infer_model(...).configure()`

### 🔗 Symlink Debugging
- Resolved `.hef` load failure by switching to absolute path using `Path(...).resolve()`, despite `ls -l` validating the symlink

### ❗ Current Status
- Model loads
- `configure()` works
- Inference still blocked — attributes like `input_streams` and `get_input_stream_infos()` missing or renamed
- Still awaiting confirmed reference usage from working tutorial

### ✅ Validated Folder Tree (as of May 4)
```bash
~/self_discovery
├── gui/
│   └── Main_App_Launch.py
├── hailort.log
├── LICENSE
├── models/
│   └── hailo/
│       └── yolov5s_personface_h8l.hef -> /usr/share/hailo-models/yolov5s_personface_h8l.hef
├── notebooks/
│   ├── devlog.md
│   ├── overview.md
│   └── setup.ipynb
├── README.md
├── requirements.txt
├── src/
│   ├── camera/
│   │   ├── camera_interface.py
│   │   └── __pycache__/
│   ├── face_detection/
│   │   ├── hailo_face_detector.py
│   │   ├── __pycache__/
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