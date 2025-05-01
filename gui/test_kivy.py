import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window

kivy.require('2.0.0')

class TestApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return Label(text="TEST", font_size=100, color=(1, 0, 0, 1)) # Red text

if __name__ == '__main__':
    TestApp().run()