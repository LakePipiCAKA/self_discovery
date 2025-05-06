#/home/taran/self_discovery/src/face_detection/hailo_face_detector.py
# src/face_detection/hailo_face_detector.py

import numpy as np
import cv2
from hailo_platform import (
    HEF,
    VDevice,
    ConfigureParams,
    HailoStreamInterface,
    InferVStreams,
    InputVStreamParams,
    OutputVStreamParams,
    FormatType,
)

class HailoFaceDetector:
    def __init__(self, hef_path):
        self.hef_path = hef_path
        self.hef = HEF(hef_path)

        # Get input shape
        self.input_info = self.hef.get_input_vstream_infos()[0]
        self.input_shape = self.input_info.shape  # (H, W, C)
        self.height, self.width = self.input_shape[:2]

        self.device = VDevice()
        self.configure_params = ConfigureParams.create_from_hef(self.hef, HailoStreamInterface.PCIe)
        self.network_group = self.device.configure(self.hef, self.configure_params)[0]

        # Params for InferVStreams
        self.input_params = InputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=FormatType.FLOAT32
        )
        self.output_params = OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=FormatType.FLOAT32
        )

        self.params = self.network_group.create_params()

    def detect_faces(self, frame, threshold=0.1):
        # Preprocess input
        resized = cv2.resize(frame, (self.width, self.height))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(normalized, axis=0)

        # Run inference
        with self.network_group.activate(self.params):
            with InferVStreams(
                self.network_group, self.input_params, self.output_params
            ) as infer_pipeline:
                input_data = {self.input_info.name: input_tensor}
                output_data = infer_pipeline.infer(input_data)
                print(f"🧪 Raw output keys: {list(output_data.keys())}")
                for k, v in output_data.items():
                    print(f"🔢 Output [{k}]: shape={np.shape(v)}, dtype={np.array(v).dtype}")

        return self._parse_output(output_data, threshold)

    def _parse_output(self, output_data, threshold):
        faces = []
        for name, output in output_data.items():
            output_array = np.array(output).astype(np.float32)

            if output_array.ndim == 4:
                batch, classes, num_detections, box_dim = output_array.shape
                if num_detections == 0:
                    print(f"⚠️ No detections: shape={output_array.shape}")
                    continue

                output_array = output_array.reshape(-1, box_dim)

            elif output_array.ndim == 2:
                if output_array.shape[1] < 6:
                    print(f"⚠️ Unexpected output shape: {output_array.shape}")
                    continue

            else:
                print(f"⚠️ Unexpected output shape: {output_array.shape}")
                continue

            for det in output_array:
                if len(det) < 5:
                    continue

                x_center, y_center, w, h, conf = det[:5]
                if conf < threshold:
                    continue

                x = int((x_center - w / 2) * self.width)
                y = int((y_center - h / 2) * self.height)
                w = int(w * self.width)
                h = int(h * self.height)

                faces.append((x, y, w, h, conf))

        print(f"👀 Parsed face detections: {faces}")
        return faces

    def close(self):
        self.device.release()

def test_from_static_image():
    import os

    test_image_path = "/home/taran/self_discovery/tests/Smart Mirror Camera Feed_screenshot_04.05.2025.png"
    if not os.path.exists(test_image_path):
        print(f"❌ Image not found: {test_image_path}")
        return

    print("📸 Loading static test image...")
    image = cv2.imread(test_image_path)

    if image is None:
        print("❌ Failed to load image. Check path or file format.")
        return

    print(f"🗾️ Original image shape: {image.shape}")
    models = [
        ("/usr/share/hailo-models/yolov5s_personface_h8l.hef", "Person+Face Model"),
        ("/usr/share/hailo-models/yolov5s_face_h8l.hef", "Face-Only Model")
    ]

    for hef_path, label in models:
        print(f"\n🔁 Testing model: {label} ({hef_path})")
        face_detector = HailoFaceDetector(hef_path)

        print(f"📏 Model expects input shape: {face_detector.input_shape}")

        resized = cv2.resize(image, (face_detector.width, face_detector.height))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(normalized, axis=0)

        print("🧪 Preprocessed tensor stats:")
        print(f"   Shape: {input_tensor.shape}")
        print(f"   dtype: {input_tensor.dtype}")
        print(f"   Min: {np.min(input_tensor):.4f}, Max: {np.max(input_tensor):.4f}, Mean: {np.mean(input_tensor):.4f}")

        print("🚀 Running inference on static image...")
        faces = face_detector.detect_faces(image)

        print(f"🎯 Detected {len(faces)} face(s)")
        for idx, (x, y, w, h, conf) in enumerate(faces):
            print(f"   🧑 Face #{idx+1}: x={x}, y={y}, w={w}, h={h}, confidence={conf:.2f}")

        face_detector.close()

if __name__ == "__main__":
    test_from_static_image()
