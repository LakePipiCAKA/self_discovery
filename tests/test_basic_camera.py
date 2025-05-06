
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.camera.camera_interface import CameraInterface

print("Testing camera interface...")
camera = CameraInterface()

print("Initializing camera...")
success = camera.initialize()
print(f"Camera initialization {'successful' if success else 'failed'}")

if success:
    print("Capturing frame...")
    frame = camera.capture_frame()
    if frame is not None:
        print(f"Captured frame with shape: {frame.shape}")
        
        # Save the frame as an image file
        import cv2
        cv2.imwrite("camera_test.jpg", frame)
        print("Saved test image as 'camera_test.jpg'")
    else:
        print("Failed to capture frame")

    print("Cleaning up...")
    camera.cleanup()
    
print("Test complete")