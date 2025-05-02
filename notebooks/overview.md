---

## 🧑‍🎨 General Use Case & Flow

When the Smart Mirror powers on (either via actual mirror hardware or a touchscreen device), it launches the main app.

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

---

### 🗂️ User Profile Management

The `user_management/` module handles the creation, storage, and retrieval of user profiles.

#### 📁 Folder Structure:
- `user_profiles.py`: Handles profile creation, loading, and updates.
- `user_profiles.json`: Local storage of user data in JSON format.

#### 🧩 Key Data Stored Per User:
- Name
- Location (city, country)
- Date of birth
- Sex
- Preferences (e.g., display tips: yes/no)
- Facial encoding or training image references

#### 🔐 Considerations:
- Profiles are stored locally — no cloud access by default.
- Future improvements may include:
  - Automatic backup or export
  - Data encryption or profile PINs
  - Face encoding stored alongside metadata

#### 🛠 Future Feature Ideas:
- Profile deletion or editing via GUI
- Profile image preview
- Profile-specific settings (theme, layout, tips frequency)

---

---

### 🧠 Face Detection Module

Located in: `src/face_detection/`

#### 📁 Files:
- `hailo_face_detector.py`: Main interface to Hailo `.hef` model using `pyhailort`
- `test_face_detector.py`: Script to test face detection pipeline
- `test_hailo.py`: Used to verify Hailo SDK installation and functionality

#### 🧩 Role:
- Loads face detection model from `models/hailo/`
- Processes camera frames to detect faces
- Returns:
  - Bounding boxes
  - Confidence scores

#### 🔜 To Do:
- Confirm `.hef` model path and structure
- Add fallback logic if Hailo device is not found
- Wrap detection in a reusable class callable by GUI or test scripts

---

### 🎛️ GUI Layer

Folders:  
- `Gui/` or `gui/`: Entry point via `Main_App_Launch.py`  
- `src/ui/`: Modular display components

#### 📁 Files in `ui/`:
- `default.py`: Possibly base layout or fallback display
- `monitoring_display.py`: Likely handles main visual overlays
- `recognition.py`: Handles face recognition hooks or confirmation
- `selection.py`, `training.py`: Used for profile creation or user interaction

#### 💡 UI Strategy:
- Built with **PyQt5**
- Display widgets **along the sides**, center remains reflective
- Dynamically update:
  - Greeting message
  - Time + weather
  - Profile-related info

#### 🛠 Potential Widgets:
- Clock and weather panel
- User greeting section
- Daily tips or alerts area
- User profile details (non-intrusive)

---

### 🌦️ Weather Integration

File: `src/weather/open_meteo.py`

#### 🔌 API Functionality:
- Calls Open-Meteo or similar weather API
- Uses:
  - Profile location (if available)
  - Manual input (City, Country) for non-profile users

#### 📊 Data Fetched:
- Current weather conditions
- Temperature
- Optional: forecast or alerts

#### 🔐 Considerations:
- Use caching to avoid rate limits
- Provide fallback display on API failure
- Normalize city/country input from GUI for cleaner requests

---

---

### 🧑‍🏫 Personalized Experience
Once a profile is created:
- Mirror uses face detection to greet the user:
  - **"Hello there {name}, you beautiful, you!"**
- Displays:
  - Time and weather (based on profile location)
  - Personalized content along the **sides of the screen**
  - Layout avoids blocking the center mirror space

---

### 📷 Facial Observation & Daily Image Capture (Future)
- Automatically captures daily images
- Tracks:
  - Skin tone changes
  - Eye white coloration
  - Pimples or blemishes
  - General "beauty health" observations
- Considerations:
  - Storage limits (local RPi storage constraints)
  - Data retention strategy

---

### 💄 Tips & Recommendations (Planned Feature)
- Targeted toward frequent female users
- At profile setup, user can **opt in to receive beauty tips**
- Future goal: Use ML to detect changes and generate personalized tips

---
