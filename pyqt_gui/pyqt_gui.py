import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Mirror")
        self.setStyleSheet("background-color: black;")
        
        # Create layout
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        
        # Time label
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("color: white; font-size: 60px;")
        self.time_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Weather label
        self.weather_label = QLabel("70°F\nWind: 5 mph")
        self.weather_label.setStyleSheet("color: lightgray; font-size: 30px;")
        self.weather_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        # Location label
        self.location_label = QLabel("Chandler, AZ")
        self.location_label.setStyleSheet("color: gray; font-size: 24px;")
        self.location_label.setAlignment(Qt.AlignCenter)
        
        # Exit instruction label
        self.exit_label = QLabel("Press ESC or Q to exit")
        self.exit_label.setStyleSheet("color: darkgray; font-size: 12px;")
        self.exit_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        
        # Add widgets to layouts
        top_layout.addWidget(self.time_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self.weather_label)
        
        main_layout.addLayout(top_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(self.location_label)
        main_layout.addWidget(self.exit_label)
        
        self.setLayout(main_layout)
        
        # Set up timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
        # Initial time update
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
    
    def update_weather(self, temperature, wind):
        self.weather_label.setText(f"{temperature}°F\nWind: {wind} mph")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Or window.showFullScreen() for Full Screen
    #window.resize(800, 600)
    sys.exit(app.exec_())