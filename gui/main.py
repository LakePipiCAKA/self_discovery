import kivy
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import datetime
import requests
import json
from kivy.core.window import Window

kivy.require('2.0.0')

class SmartMirrorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.location = "Chandler, AZ"  # Default location
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        self.latitude = 33.3152
        self.longitude = -111.8400
        self.weather_data = None

def build(self):
    root = RelativeLayout(size=Window.size)
    Window.clearcolor = (0, 0, 0, 1) # Set background to black

    # Time Label (top-left - HARDCODED POSITION AND SIZE)
    self.time_label = Label(
        text="12:00 AM",
        font_size=60,
        color=(1, 1, 1, 1),
        pos=(20, Window.height - 80), # 20 from left, 20 from top
        size_hint=(None, None),
        size=(300, 80)
    )
    root.add_widget(self.time_label)

    # Weather Label (top-right - HARDCODED POSITION AND SIZE)
    self.weather_label = Label(
        text="70°F",
        font_size=30,
        color=(1, 1, 1, 0.8),
        halign='right',
        valign='top',
        pos=(Window.width - 270, Window.height - 60), # 20 from right, 20 from top
        size_hint=(None, None),
        size=(250, 60)
    )
    root.add_widget(self.weather_label)

    # Location Label (bottom-center - HARDCODED POSITION AND SIZE)
    self.location_label = Label(
        text=self.location,
        font_size=24,
        color=(0.8, 0.8, 0.8, 1),
        halign='center',
        valign='bottom',
        pos=(Window.width / 2 - 200, 20), # Centered X, 20 from bottom
        size_hint=(None, None),
        size=(400, 40)
    )
    root.add_widget(self.location_label)

    Clock.schedule_interval(self.update_time, 1.0)
    Clock.schedule_interval(self.update_weather, 600.0)
    self.update_weather(0)

    return root

    def get_text_size(self, text, font_size):
        """Helper to get the rendered size of text."""
        label = Label(text=text, font_size=font_size)
        label.texture_update()
        return label.texture.size

    def update_time_display(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime("%I:%M:%S %p")
        # Update size based on text (with padding)
        self.time_label.size = (self.get_text_size(self.time_label.text, self.time_label.font_size)[0] + 40, self.time_label.font_size + 20)

    def fetch_weather_data(self):
        params = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current_weather': True,
            'temperature_unit': 'fahrenheit',
            'windspeed_unit': 'mph'
        }
        try:
            response = requests.get(self.weather_api_url, params=params)
            response.raise_for_status()
            self.weather_data = response.json().get('current_weather')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            self.weather_data = None

    def update_weather_data(self, dt):
        self.fetch_weather_data()
        if self.weather_data:
            temperature = self.weather_data.get('temperature')
            windspeed = self.weather_data.get('windspeed')
            self.weather_label.text = f"{temperature}°F\nWind: {windspeed} mph"
            # Update size based on text (with padding)
            self.weather_label.size = (self.get_text_size(self.weather_label.text, self.weather_label.font_size)[0] + 40, self.weather_label.font_size * 2 + 20)
        else:
            self.weather_label.text = "Weather\nUnavailable"
            self.weather_label.size = (self.get_text_size(self.weather_label.text, self.weather_label.font_size)[0] + 40, self.weather_label.font_size + 20)

if __name__ == '__main__':
    SmartMirrorApp().run()