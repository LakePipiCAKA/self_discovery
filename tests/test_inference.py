#!/home/taran/self_discovery/tests/test_inference.py - WORKS as baseline 
"""
Test inference using HailoRT with known working API calls.
"""

import sys
from hailo_platform import (
    Device,
    VDevice,
    HEF,
    ConfigureParams,
    HailoStreamInterface
)

def main():
    print("🔍 Scanning for Hailo devices...")
    devices = Device.scan()
    if not devices:
        print("❌ No Hailo devices found.")
        sys.exit(1)

    # Use absolute path to avoid file open errors
    hef_path = "/home/taran/self_discovery/models/hailo/yolov5s_personface_h8l.hef"
    print(f"📁 Loading HEF model from: {hef_path}")
    hef = HEF(hef_path)

    print("⚙️  Setting up VDevice and configuration...")
    configure_params = ConfigureParams.create_from_hef(
        hef,
        interface=HailoStreamInterface.PCIe  # or .ETH or .INTEGRATED based on your platform
    )

    with VDevice(device_ids=devices) as vdevice:
        network_groups = vdevice.configure(hef, configure_params)
        if not network_groups:
            print("❌ Failed to configure network groups.")
            return

        network_group = network_groups[0]
        print("🔌 Getting input/output stream infos...")
        input_infos = network_group.get_input_vstream_infos()
        output_infos = network_group.get_output_vstream_infos()

        print(f"✅ Found {len(input_infos)} input stream(s)")
        print(f"✅ Found {len(output_infos)} output stream(s)")

        print("🎉 Basic inference setup completed successfully!")

if __name__ == "__main__":
    main()
