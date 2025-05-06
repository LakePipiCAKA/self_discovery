#/home/taran/self_discovery/tests/camera_interface_update.py
from picamera2 import Picamera2
import cv2
import numpy as np
import time
from hailo_platform import Device, VDevice, HEF, ConfigureParams, HailoStreamInterface

class SmartMirrorCamera:
    def __init__(self, resolution=(640, 480)):
        # Initialize camera
        self.picam = Picamera2()
        self.resolution = resolution
        self.picam.preview_configuration.main.size = resolution
        self.picam.preview_configuration.main.format = "RGB888"
        self.picam.configure("preview")
        self.picam.start()
        time.sleep(1)  # Let camera warm up
        
        # Initialize Hailo face detector
        self._setup_face_detector()
        
    def _setup_face_detector(self):
        """Set up the Hailo face detection model"""
        try:
            # Find Hailo devices
            self.devices = Device.scan()
            if not self.devices:
                print("No Hailo devices found")
                self.face_detector_ready = False
                return
                
            # Load the face detection model
            model_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
            self.hef = HEF(model_path)
            
            # Get input and output info
            self.input_infos = self.hef.get_input_vstream_infos()
            self.output_infos = self.hef.get_output_vstream_infos()
            
            # Print info for debugging
            print("Input infos:", self.input_infos)
            print("Output infos:", self.output_infos)
            
            # Store input and output names
            if self.input_infos:
                self.input_name = self.input_infos[0].name
                print(f"Input name: {self.input_name}")
            else:
                raise ValueError("No input info available")
                
            if self.output_infos:
                self.output_name = self.output_infos[0].name
                print(f"Output name: {self.output_name}")
            else:
                raise ValueError("No output info available")
            
            # Get input shape - using model defaults for YOLOv5
            self.input_height = 640
            self.input_width = 640
            
            print(f"Using input dimensions: {self.input_width}x{self.input_height}")
            
            # Create VDevice and configure network
            self.vdevice = VDevice(device_ids=self.devices)
            
            configure_params = ConfigureParams.create_from_hef(
                self.hef, interface=HailoStreamInterface.PCIe)
            
            # Configure the network but do not try to create vstreams yet
            self.network_groups = self.vdevice.configure(self.hef, configure_params)
            self.network_group = self.network_groups[0]
            
            # For now, just use placeholder detection until we understand the API better
            # This will put a green box in the center of the frame
            self.face_detector_ready = True
            print("Face detector ready with placeholder detection")
            
        except Exception as e:
            print(f"Failed to initialize face detector: {e}")
            import traceback
            traceback.print_exc()
            self.face_detector_ready = False
    
    def detect_faces(self, frame):
        """Detect faces in the given frame using a placeholder detection"""
        if not self.face_detector_ready:
            return []
            
        # For now, return a placeholder detection with a box in the center
        h, w = frame.shape[:2]
        
        # Create a detection box representing ~1/4 of the frame in the center
        center_x = w // 2
        center_y = h // 2
        face_w = w // 4
        face_h = h // 4
        
        detections = [{
            'bbox': [center_x - face_w//2, center_y - face_h//2, face_w, face_h],
            'confidence': 0.95,
            'class_id': 0
        }]
        
        return detections
    
    def get_frame(self, detect_faces=False, rgb=False):
        """Get a frame from the camera, optionally with face detection"""
        frame = self.picam.capture_array()
        
        if rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        if detect_faces and self.face_detector_ready:
            # Detect faces
            faces = self.detect_faces(frame)
            
            # Draw bounding boxes
            for face in faces:
                x, y, w, h = face['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{face['confidence']:.2f}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame

    def stop(self):
        """Close camera and cleanup resources"""
        self.picam.close()
        # Clean up references
        if hasattr(self, 'vdevice'):
            self.vdevice = None
        if hasattr(self, 'network_group'):
            self.network_group = None
        if hasattr(self, 'network_groups'):
            self.network_groups = None

# Test mode
if __name__ == "__main__":
    cam = SmartMirrorCamera()
    try:
        while True:
            frame = cam.get_frame(detect_faces=True)
            cv2.imshow("Smart Mirror Camera Feed with Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.stop()
        cv2.destroyAllWindows()