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
    configured_model = infer_model.configure()  # No args

    print("🔌 Getting input/output stream infos...")
    input_infos = configured_model.get_input_vstream_infos()
    output_infos = configured_model.get_output_vstream_infos()

    print("📥 Allocating dummy input...")
    dummy_input = np.zeros(input_infos[0].shape, dtype=np.uint8)

    print("▶️ Running inference...")
    results = configured_model.infer([dummy_input])

    print("✅ Inference complete. Output shape:", results[0].shape)

if __name__ == "__main__":
    test_model_loading()
