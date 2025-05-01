
import hailo_platform
from hailo_platform import HEF

hef_path = "/usr/share/hailo-models/yolov5s_personface_h8l.hef"
hef = HEF(hef_path)

# Instead of get_input_layers, use describe()
description = hef.describe()

input_layers = description['input_tensors']
for layer in input_layers:
    print(f"Input Layer: {layer['name']}")
    print(f"Shape: {layer['shape']}")
