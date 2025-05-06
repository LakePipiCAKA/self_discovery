#!/home/taran/self_discovery/tests/test_face_detector.py
# Baseline working face detection test using Hailor + Picamera2
"""
Face detector module using Hailo platform and Picamera2 for the Smart Mirror project
"""
import sys
import os
import numpy as np
import cv2
from pathlib import Path
import time
import traceback

# Import your camera interface using the absolute path
sys.path.append(os.path.dirname("/home/taran/self_discovery/src/camera/camera_interface.py"))
from camera_interface import CameraInterface

# Import Hailo platform
from hailo_platform import (
    Device,
    VDevice, 
    HEF, 
    ConfigureParams, 
    HailoStreamInterface,
    InferVStreams,
    InputVStreamParams,
    OutputVStreamParams,
    FormatType
)

class HailoFaceDetector:
    """Face detector using Hailo AI accelerator"""
    
    def __init__(self, model_path=None, confidence_threshold=0.3):
        """Initialize the face detector"""
        if model_path is None:
            # Use the default model path
            model_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
        
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.devices = Device.scan()
        
        if not self.devices:
            raise RuntimeError("No Hailo devices found")
            
        # Load the HEF file
        self.hef = HEF(self.model_path)
        
        # Get input shape information
        self.input_vstream_info = self.hef.get_input_vstream_infos()[0]
        self.input_height, self.input_width, _ = self.input_vstream_info.shape
        
        print(f"Initialized Hailo face detector with model: {self.model_path}")
        print(f"Input shape: {self.input_width}x{self.input_height}")
    
    def detect_faces(self, frame):
        """
        Detect faces in the given frame
        
        Args:
            frame: OpenCV/numpy image in BGR format
            
        Returns:
            List of tuples (x, y, w, h, confidence) for each detected face
        """
        # Resize frame to match model input
        resized_frame = cv2.resize(frame, (self.input_width, self.input_height))
        
        # Convert to RGB (model expects RGB)
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Normalize to float32 [0-1]
        input_data = rgb_frame.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_tensor = np.expand_dims(input_data, axis=0)
        
        # Run inference
        results = self._run_inference(input_tensor)
        
        # Process detection results
        faces = self._process_detections(results, frame.shape)
        
        return faces
    
    def _run_inference(self, input_tensor):
        """Run inference on the input tensor"""
        # Create virtual device and run inference
        with VDevice(device_ids=self.devices) as vdevice:
            # Configure the network
            configure_params = ConfigureParams.create_from_hef(
                self.hef, interface=HailoStreamInterface.PCIe)
            
            # Get the network groups
            network_groups = vdevice.configure(self.hef, configure_params)
            
            # Use the first network group
            network_group = network_groups[0]
            
            # Create network_group_params
            network_group_params = network_group.create_params()
            
            # Set up input and output stream parameters
            input_vstreams_params = InputVStreamParams.make_from_network_group(
                network_group, quantized=False, format_type=FormatType.FLOAT32)
            
            output_vstreams_params = OutputVStreamParams.make_from_network_group(
                network_group, quantized=False, format_type=FormatType.FLOAT32)
            
            # IMPORTANT: Activate the network group before inference
            with network_group.activate(network_group_params):
                # Create inference streams
                with InferVStreams(network_group, 
                                input_vstreams_params, 
                                output_vstreams_params) as infer_pipeline:
                    # Prepare input data dictionary
                    input_data = {self.input_vstream_info.name: input_tensor}
                    
                    # Run inference
                    outputs = infer_pipeline.infer(input_data)
                    
                    return outputs
    
    def _process_detections(self, outputs, original_shape):
        """
        Process YOLOv5 detection outputs to extract face detections
        
        Args:
            outputs: Model output from inference
            original_shape: (height, width) of the original frame
            
        Returns:
            List of tuples (x, y, w, h, confidence) for each detected face
        """
        faces = []
        orig_h, orig_w = original_shape[:2]
        
        # Print available outputs for debugging (only on first frame)
        if getattr(self, '_first_frame', True):
            print("Available outputs:")
            for name, tensor in outputs.items():
                print(f"  {name}: type={type(tensor)}, value={tensor}")
            self._first_frame = False
        
        # The YOLOv5 NMS postprocess output is a list in the format:
        # [[person_detections_array, face_detections_array]]
        # Where each array has shape (num_detections, 5) with columns: x, y, w, h, confidence
        
        # Extract face detections from the output
        for name, output in outputs.items():
            if 'nms' in name.lower() or 'postprocess' in name.lower():
                if isinstance(output, list) and len(output) > 0:
                    # This is likely the YOLOv5 NMS output
                    try:
                        # YOLOv5 personface model has format [[person_detections, face_detections]]
                        if len(output[0]) == 2:
                            # Second element contains face detections
                            face_detections = output[0][1]
                            if hasattr(face_detections, 'shape') and face_detections.shape[0] > 0:
                                if getattr(self, '_first_detection', True):
                                    print(f"Found face detections: {face_detections.shape[0]}")
                                    self._first_detection = False
                                
                                # Process each face detection
                                for detection in face_detections:
                                    # Format is [x, y, w, h, confidence]
                                    if len(detection) >= 5:
                                        x_center, y_center, width, height, confidence = detection[:5]
                                        
                                        # Skip detections with low confidence
                                        if confidence < self.confidence_threshold:
                                            continue
                                        
                                        # Convert normalized coordinates to pixel coordinates
                                        x = int((x_center - width/2) * orig_w)
                                        y = int((y_center - height/2) * orig_h)
                                        w = int(width * orig_w)
                                        h = int(height * orig_h)
                                        
                                        # Add to face detections
                                        faces.append((x, y, w, h, confidence))
                                        
                            # Also check person detections (first element)
                            person_detections = output[0][0]
                            if hasattr(person_detections, 'shape') and person_detections.shape[0] > 0:
                                if getattr(self, '_first_person', True):
                                    print(f"Found person detections: {person_detections.shape[0]}")
                                    self._first_person = False
                                
                                # Process each person detection
                                for detection in person_detections:
                                    # Format is [x, y, w, h, confidence]
                                    if len(detection) >= 5:
                                        x_center, y_center, width, height, confidence = detection[:5]
                                        
                                        # Skip detections with low confidence
                                        if confidence < self.confidence_threshold:
                                            continue
                                        
                                        # Convert normalized coordinates to pixel coordinates
                                        x = int((x_center - width/2) * orig_w)
                                        y = int((y_center - height/2) * orig_h)
                                        w = int(width * orig_w)
                                        h = int(height * orig_h)
                                        
                                        # Uncomment to include person detections as well
                                        # faces.append((x, y, w, h, confidence))
                    except Exception as e:
                        print(f"Error processing detections: {e}")
        
        return faces

# Simple demo/test code
if __name__ == "__main__":
    import sys
    
    try:
        # Create face detector with lower confidence threshold for testing
        face_detector = HailoFaceDetector(confidence_threshold=0.3)
        
        # Initialize camera using your interface
        print("Initializing camera...")
        camera = CameraInterface()
        
        print("Camera started")
        
        print("Press 'q' to quit")
        
        # Main loop
        while True:
            try:
                # Capture a frame (note: get_frame returns in BGR format by default)
                frame = camera.get_frame()
                
                # Detect faces
                faces = face_detector.detect_faces(frame)
                
                # Draw faces on frame
                for x, y, w, h, conf in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Face: {conf:.2f}", (x, y-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Display result
                cv2.imshow("Hailo Face Detection", frame)
                
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                print("Interrupted by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                traceback.print_exc()
                # Continue with the next frame instead of breaking
                continue
        
        # Clean up
        cv2.destroyAllWindows()
        camera.stop()
        print("Camera stopped")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()