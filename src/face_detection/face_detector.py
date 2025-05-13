# /home/taran/self_discovery/src/face_detection/face_detector.py
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

    def detect_faces(self, frame, threshold=0.4):
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

        return self.postprocess(output_dict)

    def non_max_suppression(self, boxes, iou_threshold=0.4):
        if len(boxes) == 0:
            return []

        boxes = sorted(boxes, key=lambda x: x[4], reverse=True)
        selected_boxes = []

        def iou(box1, box2):
            x1, y1, w1, h1 = box1[:4]
            x2, y2, w2, h2 = box2[:4]
            xa = max(x1, x2)
            ya = max(y1, y2)
            xb = min(x1 + w1, x2 + w2)
            yb = min(y1 + h1, y2 + h2)
            inter_area = max(0, xb - xa) * max(0, yb - ya)
            union_area = w1 * h1 + w2 * h2 - inter_area
            return inter_area / union_area if union_area > 0 else 0

        while boxes:
            current = boxes.pop(0)
            selected_boxes.append(current)
            boxes = [box for box in boxes if iou(current, box) < iou_threshold]

        return selected_boxes

    def postprocess(self, output_dict, threshold=0.4):
        detections = []
        input_w, input_h = self.input_shape[1], self.input_shape[0]

        for name, output_list in output_dict.items():
            for item in output_list:
                nested_items = item if isinstance(item, list) else [item]
                for subitem in nested_items:
                    if isinstance(subitem, np.ndarray):
                        rows = subitem.reshape(-1, subitem.shape[-1])
                        for row in rows:
                            if len(row) < 5:
                                continue
                            x1, y1, x2, y2, score = row[:5]
                            if score < threshold:
                                continue
                            x1 = max(0, int(x1 * input_w))
                            y1 = max(0, int(y1 * input_h))
                            x2 = min(input_w - 1, int(x2 * input_w))
                            y2 = min(input_h - 1, int(y2 * input_h))
                            w = x2 - x1
                            h = y2 - y1
                            if w > 0 and h > 0:
                                detections.append((x1, y1, w, h, float(score)))
                    else:
                        print(f"[WARN] Skipped subitem of type {type(subitem)}")

        return self.non_max_suppression(detections)

    def close(self):
        self.vdevice.release()
