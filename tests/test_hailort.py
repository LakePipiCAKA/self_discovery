#! /home/taran/self_discovery/tests/test_hailort.py - works as baseline
"""
Test Hailo platform API with working imports
"""
import sys
print(f"Python version: {sys.version}")

# Import from hailo_platform which we verified works
from hailo_platform import (
    Device,
    VDevice, 
    HEF, 
    ConfigureParams, 
    HailoStreamInterface
)

def test_device_scan():
    try:
        # Scan for devices
        devices = Device.scan()
        print(f"Found {len(devices)} Hailo device(s)")
        
        for i, device_id in enumerate(devices):
            print(f"Device {i}: {device_id}")
        
        return devices
    except Exception as e:
        print(f"Error scanning for devices: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_load_model(devices):
    if not devices:
        print("No devices available")
        return False
    
    try:
        # Path to the model file
        model_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
        
        # Load HEF file
        print(f"Loading model from {model_path}")
        hef = HEF(model_path)
        
        # Create virtual device
        print("Creating VDevice")
        with VDevice(device_ids=devices) as vdevice:
            # Configure the network
            print("Configuring network")
            configure_params = ConfigureParams.create_from_hef(
                hef, interface=HailoStreamInterface.PCIe)
            
            # Get the network group
            print("Getting network groups")
            network_groups = vdevice.configure(hef, configure_params)
            print(f"Network groups: {network_groups}")
            
            print("Successfully configured model!")
            return True
            
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # First, scan for devices
    devices = test_device_scan()
    
    # If devices found, try to load a model
    if devices:
        success = test_load_model(devices)
        return success
    else:
        return False

if __name__ == "__main__":
    success = main()
    print(f"Test {'passed' if success else 'failed'}")