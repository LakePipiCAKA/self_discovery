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

        self.network_group_params = self.network_group.create_params()

        self.input_infos = self.network_group.get_input_stream_infos()
        self.output_infos = self.network_group.get_output_stream_infos()
        self.input_name = self.input_infos[0].name
        self.output_name = self.output_infos[0].name

        self.input_params = hailort.InputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=hailort.FormatType.UINT8
        )
        self.output_params = hailort.OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=hailort.FormatType.FLOAT32
        )

        self.input_shape = self.input_infos[0].shape[:2]  # (height, width)

    def detect_faces(self, frame):
        resized = cv2.resize(frame, (self.input_shape[1], self.input_shape[0]))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        input_tensor = rgb.astype(np.uint8).flatten()
        input_tensor = np.expand_dims(input_tensor, axis=0)
        input_dict = {self.input_name: input_tensor}

        with self.network_group.activate(self.network_group_params):
            with hailort.InferVStreams(
                self.network_group, self.input_params, self.output_params
            ) as streams:
                output_dict = streams.infer(input_dict)

        # DEBUG: Inspect raw Hailo output
        for key, val in output_dict.items():
            print(
                f"[HAILO DEBUG] Output key: {key}, type: {type(val)}, length: {len(val)}"
            )
            if isinstance(val, list) and len(val) > 0:
                first = val[0]
                print(
                    f"[HAILO DEBUG] First item type: {type(first)}, length: {len(first) if isinstance(first, (bytes, bytearray)) else 'INVALID'}"
                )

        return self.postprocess(output_dict)

    def postprocess(self, output_dict, threshold=0.3):
        detections = []
        input_w, input_h = self.input_shape[1], self.input_shape[0]

        for name, output_list in output_dict.items():
            for item in output_list:
                if isinstance(item, list):
                    for det in item:
                        if isinstance(det, np.ndarray):
                            rows = det.reshape(-1, det.shape[-1])
                            for row in rows:
                                if len(row) < 5:
                                    continue
                            try:
                                x1, y1, x2, y2, score = row[:5]
                            except ValueError:
                                continue
                            if score < threshold:
                                continue

                            # Scale to image size and clip to bounds
                            x1 = max(0, int(x1 * input_w))
                            y1 = max(0, int(y1 * input_h))
                            x2 = min(input_w - 1, int(x2 * input_w))
                            y2 = min(input_h - 1, int(y2 * input_h))
                            w = x2 - x1
                            h = y2 - y1

                            if w > 0 and h > 0:
                                detections.append((x1, y1, w, h, float(score)))

        return detections

    def close(self):
        self.vdevice.release()
