# src/face_detection/hailo_face_detector.py

import hailo_platform as hailort
import cv2
import numpy as np

class HailoFaceDetector:
    def __init__(self, hef_path):
        self.hef_path = hef_path
        self.vdevice = hailort.VDevice()
        self.hef = hailort.HEF(hef_path)
        self.network_groups = self.vdevice.configure(self.hef)
        self.network_group = self.network_groups[0]  # Assume one network group

        # Get input and output names
        self.input_name = self.network_group.get_input_stream_infos()[0].name
        self.output_name = self.network_group.get_output_stream_infos()[0].name

        # Create input/output virtual streams
        self.input_vstream = self.network_group.create_input_vstream(self.input_name)
        self.output_vstream = self.network_group.create_output_vstream(self.output_name)

        # Assume model expects 640x640 input (adjust later if needed)
        self.input_shape = (640, 640)

    def preprocess(self, frame):
        # Resize to model input size
        resized = cv2.resize(frame, self.input_shape)

        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Normalize if needed (depends on training, we assume 0-255 for now)
        normalized = rgb.astype(np.uint8)  # model expects uint8

        # Hailo expects NHWC flattened to 1D array
        return normalized.flatten()

    def postprocess(self, raw_output, threshold=0.5):
        # Very basic: assume YOLOv5-like output parsing
        detections = []

        num_classes = 1  # face class only
        num_anchors = 25200  # depends on model structure
        stride = (num_classes + 5)

        output = np.frombuffer(raw_output, dtype=np.float32)

        for i in range(num_anchors):
            obj_score = output[i * stride + 4]
            if obj_score > threshold:
                x_center = output[i * stride + 0]
                y_center = output[i * stride + 1]
                width = output[i * stride + 2]
                height = output[i * stride + 3]

                # Convert from center format to top-left corner
                x = int((x_center - width/2) * self.input_shape[0])
                y = int((y_center - height/2) * self.input_shape[1])
                w = int(width * self.input_shape[0])
                h = int(height * self.input_shape[1])

                detections.append((x, y, w, h))

        return detections

    def detect_faces(self, frame):
        preprocessed = self.preprocess(frame)

        # Send input frame
        self.input_vstream.send(preprocessed)

        # Receive output
        raw_output = self.output_vstream.receive()

        # Debug output buffer
        float_output = np.frombuffer(raw_output, dtype=np.float32)
        print("Raw output shape:", float_output.shape)
        print("First 20 values:", float_output[:20])

        # Postprocess to get bounding boxes
        boxes = self.postprocess(raw_output)

        return boxes

    def close(self):
        self.input_vstream.close()
        self.output_vstream.close()
        self.vdevice.close()
