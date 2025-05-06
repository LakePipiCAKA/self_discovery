#!/usr/bin/env python3
"""
Test Hailo integration for Smart Mirror project
"""
import sys
print(f"Python version: {sys.version}")

try:
    # Try importing from hailo_platform first (recommended)
    from hailo_platform import (
        Device,
        VDevice, 
        HEF, 
        ConfigureParams, 
        HailoStreamInterface
    )
    print("Successfully imported hailo_platform")
    
    # Check for devices
    try:
        devices = Device.scan()
        print(f"Found {len(devices)} Hailo device(s)")
        
        for i, device_id in enumerate(devices):
            print(f"Device {i}: {device_id}")
    except Exception as e:
        print(f"Error scanning for devices: {e}")
        
    # Test model loading
    try:
        model_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
        print(f"Loading model from {model_path}")
        hef = HEF(model_path)
        print("HEF loaded successfully")
        
        # Test virtual device creation
        if devices:
            print("Creating VDevice")
            vdevice = VDevice(device_ids=devices)
            print(f"VDevice created: {vdevice}")
            
            # Test configuration
            print("Testing configuration")
            configure_params = ConfigureParams.create_from_hef(
                hef, interface=HailoStreamInterface.PCIe)
            print("Configuration parameters created")
            
            print("All tests passed - Hailo is ready for your Smart Mirror project!")
        else:
            print("No devices available to test VDevice creation")
    except Exception as e:
        print(f"Error in model loading or configuration: {e}")
        import traceback
        traceback.print_exc()

except ImportError:
    print("hailo_platform is not installed, trying pyhailort as fallback...")
    
    # Try with pyhailort as fallback
    try:
        import pyhailort
        print(f"pyhailort is installed, version: {pyhailort.__version__ if hasattr(pyhailort, '__version__') else 'unknown'}")
        
        # Try to import some key components from pyhailort
        from pyhailort import PyhailortException, Device, VDevice
        print("Successfully imported key pyhailort components")
        
        # Check if hardware is detected
        try:
            device = Device()
            print(f"Hardware Hailo device found: {device}")
        except Exception as e:
            print(f"No hardware device found: {e}")
            
        # Check if virtual device works
        try:
            vdevice = VDevice()
            print(f"Virtual device created: {vdevice}")
        except Exception as e:
            print(f"Failed to create virtual device: {e}")
            
    except ImportError:
        print("Neither hailo_platform nor pyhailort are installed.")
        print("Please install the correct Hailo Python bindings for your Smart Mirror project.")
        print("Recommendation: Use hailo_platform as shown in your working test_hailort.py")