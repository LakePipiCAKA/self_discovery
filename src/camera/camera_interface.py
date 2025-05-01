# src/camera/camera_interface.py
from picamera2 import Picamera2
import numpy as np
import cv2

class CameraInterface:
    def __init__(self):
        self.camera = None
        self.is_initialized = False
        
    def initialize(self):
        try:
            self.camera = Picamera2()
            # Configure for optimal face detection
            config = self.camera.create_still_configuration(
                main={"size": (640, 480)},
                buffer_count=1
            )
            self.camera.configure(config)
            self.camera.start()
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def capture_frame(self):
        """Capture a single frame for face detection"""
        if not self.is_initialized:
            if not self.initialize():
                return None
                
        try:
            frame = self.camera.capture_array()
            # Convert to BGR for OpenCV compatibility if needed
            if frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            return frame
        except Exception as e:
            print(f"Frame capture failed: {e}")
            return None
    
    def cleanup(self):
        """Clean up camera resources"""
        if self.camera and self.is_initialized:
            self.camera.stop()
            self.camera.close()
            self.is_initialized = False