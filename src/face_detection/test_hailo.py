# src/face_detection/test_hailo.py
import hailo_platform
from hailo_platform import Device, HEF, ConfigureParams

print("Hailo Platform Version:", hailo_platform.__version__)
print("All available attributes in hailo_platform:", dir(hailo_platform))

try:
    # Basic device initialization
    device = Device()
    print("Device initialized successfully")
    
    # Try to load HEF without interface parameter
    hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
    hef = HEF(hef_path)
    print("HEF loaded successfully")
    
    # Simple configuration without interface
    configure_params = ConfigureParams.create_from_hef(hef)
    print("ConfigureParams created successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()