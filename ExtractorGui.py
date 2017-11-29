from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button

class ExtractorGuiApp(App):
    def build_config(self, config):
        config.setdefaults('Email', {
            'IMAP_HOST': 'imap.gmail.com',
        })



ExtractorGuiApp().run()
