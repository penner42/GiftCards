from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.settings import SettingString
from Extract import Extract
from Barcode import Barcode
from Swipe import Swipe
import os, sys
from kivy.lang.builder import Builder

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_path(self):
        return os.path.expanduser("~")

class GiftCards(TabbedPanel):
    pass


class PasswordLabel(Label):
    pass


class SettingPassword(SettingString):
    def _create_popup(self, instance):
        super(SettingPassword, self)._create_popup(instance)
        self.textinput.password = True

    def add_widget(self, widget, *largs):
        if self.content is None:
            super(SettingString, self).add_widget(widget, *largs)
        if isinstance(widget, PasswordLabel):
            return self.content.add_widget(widget, *largs)


class CommonWidgets(BoxLayout):
    def exit(self):
        sys.exit()

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""

class GiftCardsApp(App):
    def resource_path(self, relative_path=None):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        if relative_path:
            return os.path.join(base_path, relative_path)
        else:
            return base_path

    def build_config(self, config):
        config.setdefaults('Settings', {'chromedriver_path': '', 'days': 1, 'selected_source': 'Paypal Digital Gifts', 'hide_chrome_window': 1, 'screenshots': 0})
        config.setdefaults('Email1', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': '','phonenum': ''})
        config.setdefaults('Email2', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': '','phonenum': ''})
        config.setdefaults('Email3', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': '','phonenum': ''})
        config.setdefaults('Email4', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': '','phonenum': ''})

    def build_settings(self, settings):
        settings.register_type('password', SettingPassword)
        settings.add_json_panel('Settings', self.config, self.resource_path('Settings/ExtractorSettings.json'))
        settings.add_json_panel('Emails', self.config, self.resource_path('Settings/ExtractorEmails.json'))

    def close_settings(self, settings=None):
        self._tabbedpanel.switch_to(self._current_tab)
        super(GiftCardsApp, self).close_settings(settings)

    def open_settings(self):
        self._current_tab = self._tabbedpanel.current_tab
        super(GiftCardsApp, self).open_settings()

    def build(self):
        # This seems to be necessary for things to load properly in Linux
        if sys.platform == 'linux':
            Builder.load_file('GiftCards.kv')

        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        self._extract = Extract.Extract()
        self._swipe = Swipe.Swipe()
        self._barcode = Barcode.Barcode()
        self._extract.build()

        inp = GiftCards(do_default_tab=False)
        th = TabbedPanelHeader(text='Extract')
        th.content = self._extract
        th.bind(on_release=lambda instance: self._extract.selected())
        inp.add_widget(th)
        th = TabbedPanelHeader(text='Swipe')
        th.content = self._swipe
        th.bind(on_release=lambda instance: self._swipe.selected())
        inp.add_widget(th)
        th = TabbedPanelHeader(text='Barcode')
        th.content = self._barcode
        th.bind(on_release=lambda instance: self._barcode.selected())
        inp.add_widget(th)
        th = TabbedPanelHeader(text='Settings')
        th.bind(on_release=lambda instance: self.open_settings())
        inp.add_widget(th)
        self._tabbedpanel = inp
        return inp


GiftCardsApp().run()
