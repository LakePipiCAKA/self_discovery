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

## Resolved

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
# Devlog Update - Project Structure Overview

As part of the ongoing development of the `self_discovery` project, here's the current directory structure (up to 5 levels deep) to document the organization of code, models, and tests. This snapshot was generated using `tree -L 5` from the project root:

```bash
.
├── gui
│   └── Main_App_Launch.py
├── hailort.1.log
├── hailort.log
├── LICENSE
├── models
│   └── hailo
│       └── yolov5s_personface_h8l.hef
├── notebooks
│   ├── devlog.md
│   ├── overview.md
│   └── setup.ipynb
├── README.md
├── requirements.txt
├── src
│   ├── camera
│   │   ├── camera_interface.py
│   │   └── __pycache__
│   │       └── camera_interface.cpython-311.pyc
│   ├── face_detection
│   │   ├── hailo_face_detector.py
│   │   ├── hailo_runtime.py
│   │   └── __pycache__
│   │       └── hailo_face_detector.cpython-311.pyc
│   ├── ui
│   │   ├── default.py
│   │   ├── monitoring_display.py
│   │   ├── recognition.py
│   │   ├── selection.py
│   │   └── training.py
│   ├── user_management
│   │   ├── user_profiles.json
│   │   └── user_profiles.py
│   └── weather
│       └── open_meteo.py
└── tests
    ├── test_basic_camera.py
    ├── test_face_detector.py
    ├── test_hailort.py
    └── test_inference.py

14 directories, 27 files
```
### Progres Update May 4th 2025
# Inferences works, hailor API works 
```
```
### Face Detection Static Image Test — May 4, 2025

- Added `test_from_static_image()` to `hailo_face_detector.py`
- Image used for test: `/home/taran/self_discovery/tests/Smart Mirror Camera Feed_screenshot_04.05.2025.png`
- Tested both `.hef` models:
  - `yolov5s_personface_h8l.hef`
  - `yolov5s_face_h8l.hef`
- Preprocessing steps applied:
  - Resize to expected input shape
  - BGR → RGB color conversion
  - Normalization and reshaping to `[1, H, W, C]`
- Output consistently returned shape `(1, 2, 0, 5)` → **No detections**

#### ⚠️ Current Blocker

- Output tensor has unexpected shape: `(1, 2, 0, 5)`
- `InferVStreams` returns empty results
- Parser fails with: "inhomogeneous shape after 2 dimensions"

#### 🔍 Diagnosis Summary

- Confirmed PiSP uses RGB888 format
- Test image lighting consistent with working live detection scripts
- Input preprocessing matches Hailo documentation
- Still fails to produce detections across both `.hef` models

#### 🧭 Next Steps

1. ✅ Port structure from `HRT_0_Async_Inference_Tutorial.ipynb` into this project
2. 🧪 Try alternate `.hef` models bundled with SDK demos
3. 🔄 Revisit and log `input_info.name`, shape, and expected layout (NCHW/NHWC)
4. 🧹 Option: Switch to OpenCV-based detection temporarily for profile creation

```

Resuming next time with streamlined flow from tested Hailo async inference tutorial.

```
#### PHASE 1: Clean-Up & Minor Refactors
# Confirm directory consistency

- Ensure data/users/ will be the default place for user image data, profile images, health snapshots, etc.

- Keep src/user_management/user_profiles.json as the user index (you already use this for metadata).

# Refactor filenames for clarity (no logic change yet)

- Rename hailo_face_detector_flat.py → hailo_face_detector_display.py if it's only for display/debug use.

- Rename default.py in ui/ → welcome.py or start_screen.py (matches behavior).

- Consider merging monitoring_display.py, recognition.py, and selection.py if they're small and used only for profile interaction. If not, leave as is.

# Update README and overview.md accordingly
-------------------------------------- A little housekeeping-----------------------------
#### PHASE 2: Logic Isolation & Safety
# Split model load logic

Move the HailoFaceDetector initialization logic into a helper in face_detection/__init__.py to avoid repetition and future risk.

Add logging inside the class for better debugging (self.logger = logging.getLogger(...) if needed).

# Consolidate weather logic

Move get_weather() from main_app_launch.py into weather/open_meteo.py and import it.

#### PHASE 3: Main App Improvements (lightweight)
# Implement "no user → prompt create user" logic

On startup, check if user_profiles.json is empty or contains only defaults.

If no user: show prompt with button: “Create new user” and bring up name/location input fields (can be a QDialog or added view).

This can be done inside update_time_weather() or as a one-time check during __init__().

# Store profile photos

On new user creation or detection, create folder under data/users/<username>/

Save detection snapshot (face image) with timestamp.

Plan a retention policy (e.g., one image per day max, or overwrite).

#### PHASE 4: Future (but simple) Additions
# Enable health tracking placeholder

Add a method stub in user_analysis/track_changes.py with def analyze_face_history(user_id) returning mock values (e.g., “No change”).

Later plug in OpenCV-based comparison or ML skin detection.

# Prepare SQLite fallback (optional)

If JSON grows painful, convert user_profiles.json logic to sqlite3 with same schema (name, location, photo paths).

Not needed now, but structure things to make switch painless.
----------------------------------- House Keeping ends -----------------------------------

#### 2025-05-06 — Face Detection, User Creation Prompt, and Project Cleanup
# System Status:

- App launches successfully from main_app_launch.py.

- PyQt5 GUI displays camera feed, time, and weather.

- Hailo-accelerated face detection confirmed active via green bounding boxes.

- User-facing labels update based on presence/absence of face.

# Major Progress:

✅ Integrated face-based presence detection in main_app_launch.py.

✅ Camera blur activates when no face detected.

✅ Added greeting label toggle between "👋 Hello there!" and "😴 Waiting for face...".

✅ JSON-based user registration logic implemented using user_profiles.json.

✅ Automatic prompt for new user creation when no valid registered users found.

✅ Cleaned up old fake profiles by filtering on "registered": true flag.

✅ Updated and validated user_profiles.py functions (load_profiles, save_profile).

✅ Resolved Qt plugin crash during GUI launch caused by system config mismatch.

✅ Confirmed use of HailoFaceDetector (not OpenCV/CPU fallback).

# Refactoring / Structure:

- Reviewed current folder tree and preserved all working scripts.

- Agreed on deferred full cleanup until core flow is functional.

- user_profiles.json now expected to contain "registered": true for valid users.

# Next Priorities:

 - Implement logic to recognize existing faces and map them to registered users.

 - Offer greeting with user name when recognized.

 - Begin saving facial snapshots with date and metadata under /data/users/{username}/.

 - Update GUI to show image history (simple left/right nav).

 - Begin preparing user_analysis scaffolding for future weight/skin tracking.

------------------------------------------------------------------------
#### Additional for 5/6

# ✅ Major Progress Today

- main_app_launch.py now:

- Prompts for user creation if no users exist in user_profiles.json

- Displays camera feed with live face detection using Hailo hardware

- Shows time and weather (fallback to "N/A" if API fails)

- Applies Gaussian blur to the video feed if no face is detected

- Successfully tested GUI from VS Code terminal — verified green bounding boxes follow face

- Verified Hailo accelerator (not CPU fallback like Haar cascades) is in use

# JSON Schema & Profile Enhancements

- user_profiles.json now expected to hold:

-      name, location, dob, sex, preferences, snapshots

-Created and integrated create_new_user() in user_profiles.py to align new user structure with project goals

# Folder Structure

- Reviewed and aligned current folder layout:

  - src/ still houses modular logic (camera, UI, face detection, etc.)

  - data/users/ directory will hold future user-specific snapshots

  - notebooks/overview.md updated for consistency with implemented features

# ⚠️ Notes

- First-time user registration currently uses a pop-up (QInputDialog) — future improvement will be GUI-only inside the mirror display

- user_profiles.json must start empty {} to allow prompting

- No face profile matching/recognition logic active yet — only detection via Hailo YOLOv5s model
- ----------------------------------------------------------

### [Update] UI Folder Removed
- Removed unused `src/ui/` folder to simplify structure.
- All logic now lives in:
  - `gui/` for the main application launcher and integration
  - `user_management/` for profile, snapshot, embedding, and recognition
  - `face_detection/` for Hailo detection logic
  - `camera/` for camera stream handling
  - `data/users/` for storing snapshots
