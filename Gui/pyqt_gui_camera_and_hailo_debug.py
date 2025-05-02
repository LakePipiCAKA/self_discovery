# pyqt_gui/pyqt_gui_camera_and_hailo_debug.py
import sys
import os
print("Starting debug script...")

try:
    # Add debug path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("Path added successfully")
    
    # Try imports one by one
    print("Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
    from PyQt5.QtCore import Qt, QTimer
    
    print("Importing datetime...")
    from datetime import datetime
    
    print("Importing camera interface...")
    from src.camera.camera_interface import CameraInterface
    
    print("Importing hailo face detector...")
    from src.face_detection.hailo_face_detector import HailoFaceDetector
    
    print("All imports successful!")
    
    # Now try to create the application
    print("Creating application...")
    app = QApplication(sys.argv)
    
    print("Creating main window...")
    window = MainWindow()  # This will fail if MainWindow class wasn't properly defined
    
    print("Showing window...")
    window.show()
    
    print("Starting event loop...")
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()