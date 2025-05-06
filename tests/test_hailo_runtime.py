# src/face_detection/hailo_runtime.py

from hailo_platform import Device, VDevice, HEF, ConfigureParams, HailoStreamInterface

def scan_hailo_devices():
    return Device.scan()

def load_model_on_vdevice(model_path="/usr/share/hailo-models/yolov5s_personface_h8l.hef", interface=HailoStreamInterface.PCIe):
    devices = scan_hailo_devices()
    if not devices:
        raise RuntimeError("No Hailo devices found")
    
    hef = HEF(model_path)
    vdevice = VDevice(device_ids=devices)

    configure_params = ConfigureParams.create_from_hef(hef, interface=interface)
    network_groups = vdevice.configure(hef, configure_params)
    return vdevice, hef, network_groups[0]

if __name__ == "__main__":
    print("🔁 Running standalone model load test...")
    vdevice, hef, network_group = load_model_on_vdevice()
    print("✅ Model loaded and VDevice created successfully.")
