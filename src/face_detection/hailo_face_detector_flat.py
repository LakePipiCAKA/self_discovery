# /home/taran/self_discovery/src/face_detection/hailo_face_detector.py

import hailo_platform as hailort
import cv2
import numpy as np

class HailoFaceDetector:
    def __init__(self, hef_path):
        self.hef_path = hef_path
        self.vdevice = hailort.VDevice()
        self.hef = hailort.HEF(hef_path)
        self.network_groups = self.vdevice.configure(self.hef)
        self.network_group = self.network_groups[0]

        # Configure model
        self.network_group_params = self.network_group.create_params()

        self.input_infos = self.network_group.get_input_stream_infos()
        self.output_infos = self.network_group.get_output_stream_infos()
        self.input_name = self.input_infos[0].name
        self.output_name = self.output_infos[0].name

        # Input/output stream params
        self.input_params = hailort.InputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=hailort.FormatType.UINT8)
        self.output_params = hailort.OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=hailort.FormatType.FLOAT32)

        self.input_shape = self.input_infos[0].shape[:2]  # (height, width)

    def detect_faces(self, frame):
        resized = cv2.resize(frame, (self.input_shape[1], self.input_shape[0]))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        input_tensor = rgb.astype(np.uint8).flatten()

        with self.network_group.activate(self.network_group_params):
            with hailort.InferVStreams(self.network_group, self.input_params, self.output_params) as streams:
                input_dict = {self.input_name: input_tensor}
                output_dict = streams.infer(input_dict)

        return self.postprocess(output_dict)

    def postprocess(self, output_dict, threshold=0.4):
        detections = []
        for name, raw_output in output_dict.items():
            data = np.frombuffer(raw_output, dtype=np.float32)
            stride = 6  # x, y, w, h, obj, class
            for i in range(0, len(data), stride):
                obj_score = data[i + 4]
                if obj_score < threshold:
                    continue

                x_center, y_center, w, h = data[i:i+4]
                x = int((x_center - w/2) * self.input_shape[1])
                y = int((y_center - h/2) * self.input_shape[0])
                w = int(w * self.input_shape[1])
                h = int(h * self.input_shape[0])
                detections.append((x, y, w, h, obj_score))
        return detections

    def close(self):
        self.vdevice.release()
