from hailo_platform import VDevice
import numpy as np

def test_model_loading():
    print("🔧 Creating VDevice...")
    vdevice = VDevice()

    hef_path = "models/hailo/yolov5s_personface_h8l.hef"
    print(f"📁 Loading model from: {hef_path}")

    print("📦 Creating InferModel...")
    infer_model = vdevice.create_infer_model(hef_path)

    print("⚙️  Configuring model with default params...")
    configured_model = infer_model.configure()
    configured_model.create_bindings()

    input_vstream = configured_model.input_vstreams[0]
    output_vstream = configured_model.output_vstreams[0]

    print("📥 Preparing dummy input...")
    input_shape = input_vstream.get_frame_shape()
    dummy_input = np.zeros(input_shape, dtype=np.uint8)

    print("▶️ Sending dummy input...")
    input_vstream.send(dummy_input)

    print("📤 Receiving output...")
    output = output_vstream.recv()

    print("✅ Inference complete. Output shape:", output.shape)

if __name__ == "__main__":
    test_model_loading()
