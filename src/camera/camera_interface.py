from picamera2 import Picamera2
import cv2
import numpy as np
import time

class CameraInterface:
    def __init__(self, resolution=(640, 480)):
        self.picam = Picamera2()
        self.resolution = resolution
        self.picam.preview_configuration.main.size = resolution
        self.picam.preview_configuration.main.format = "RGB888"
        self.picam.configure("preview")
        self.picam.start()
        time.sleep(1)  # Let camera warm up

    def get_frame(self, rgb=False):
        frame = self.picam.capture_array()
        if rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        return frame #default is BGR

    def stop(self):
        self.picam.close()

# Test mode
if __name__ == "__main__":
    cam = CameraInterface()
    try:
        while True:
            frame = cam.get_frame()
            #frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) --made skin look blue
            cv2.imshow("Smart Mirror Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.stop()
        cv2.destroyAllWindows()
