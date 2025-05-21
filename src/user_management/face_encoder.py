# /home/taran/self_discovery/src/user_management/face_encoder.py
# Supports both Hailo-accelerated embedding (when available) and CPU fallback

import numpy as np
import cv2

try:
    import face_recognition

    has_face_recognition = True
except ImportError:
    has_face_recognition = False

# Placeholder for future Hailo integration
USE_HAILO = False


# === Matching ===
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def is_match(vec1, vec2, threshold=0.5):
    return cosine_similarity(vec1, vec2) > (1 - threshold)


# === Encoding ===
def extract_embedding(frame_bgr):
    """
    Extract a 128D face embedding from a given frame using either Hailo or CPU fallback.
    Returns None if no face is detected.
    """
    if USE_HAILO:
        # Placeholder: Use Hailo infer() call once .hef is compiled
        raise NotImplementedError("Hailo embedding not yet integrated.")

    elif has_face_recognition:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        if not face_locations:
            return None
        encodings = face_recognition.face_encodings(rgb, face_locations)
        return encodings[0] if encodings else None

    else:
        raise RuntimeError("No available embedding backend (Hailo or face_recognition)")
