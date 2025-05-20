import cv2
import numpy as np
import os


def analyze_face_history(user_id, snapshot_folder):
    snapshots = sorted([f for f in os.listdir(snapshot_folder) if f.endswith(".jpg")])[
        -3:
    ]

    if not snapshots:
        return "⚠️ Not enough data to analyze."

    avg_brightness = []
    for snap in snapshots:
        img = cv2.imread(os.path.join(snapshot_folder, snap))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        avg_brightness.append(np.mean(gray))

    diff = max(avg_brightness) - min(avg_brightness)
    mean_brightness = np.mean(avg_brightness)

    if mean_brightness < 80:
        return "😓 Your skin looks a bit dull. Hydrate and try a brightening routine."
    elif diff > 15:
        return "☀️ Skin tone looks uneven. Try a calming mask or reduce sun exposure."
    else:
        return "😊 Skin looks consistent. Keep it up!"
