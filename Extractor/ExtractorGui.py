from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.dropdown import DropDown
from Extractor.extractors import extractors_list
from kivy.uix.settings import SettingString
from kivy.uix.label import Label
from imaplib import IMAP4, IMAP4_SSL
from datetime import datetime, timedelta, date
from selenium import webdriver
from kivy.clock import Clock, mainthread
from bs4 import BeautifulSoup
import email
import threading

import os

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

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def get_path(self):
        return os.path.expanduser("~")

class InputWindow(BoxLayout):

    def clear_release(self, value):
        if value == "normal":
            self.ids.csv_output.text = ""

    def copy_output(self, value):
        if value == "normal":
            Clipboard.copy(self.ids.csv_output.text)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.ids.csv_output.text)

        self.dismiss_popup()

    @mainthread
    def update_progress(self, text, value=0):
        self.popup.progresslabel.text = text

    def extract_cards(self):
        progresslabel = Label(id='progresslabel', text='extracting')
        self.popup = Popup(title='extracting', content=progresslabel, size_hint=(.5,.5), auto_dismiss=False)
        self.popup.progresslabel = progresslabel
        self.popup.open()
        threading.Thread(target=self.extract_cards_real).start()

    def extract_cards_real(self):
        a = App.get_running_app()
        config = a.config
        extractor = None
        cards = {}
        urls = []

        e = [x for x in extractors_list if x.name() == a.window.ids.dropdownbtn.text]
        if len(e) == 1:
            extractor = e[0]()
        else:
            # TODO: show error about no card source selected
            return
        days = int(config.get('Settings', 'days'))
        browser = None
        for section in ['Email1', 'Email2', 'Email3', 'Email4']:
            if int(config.get(section, 'imap_active')) == 1:
                imap_ssl = int(config.get(section, 'imap_ssl')) == 1
                imap_host = config.get(section, 'imap_host')
                imap_port = int(config.get(section, 'imap_port'))
                imap_username = config.get(section, 'imap_username')
                imap_password = config.get(section, 'imap_password')
                # Connect to the server
                if imap_ssl:
                    mailbox = IMAP4_SSL(host=imap_host, port=imap_port)
                else:
                    mailbox = IMAP4(host=imap_host, port=imap_port)

                # Log in and select the configured folder
                mailbox.login(imap_username, imap_password)
                mailbox.select("INBOX")
                since = (date.today() - timedelta(days - 1)).strftime("%d-%b-%Y")
                status, messages = mailbox.search(None,'(FROM {})'.format(extractor.email()) + ' SINCE ' + since)
                if status == "OK":
                    # Convert the result list to an array of message IDs
                    messages = messages[0].split()
                    for msg_id in messages:
                        self.update_progress("---> Processing message id {}...".format(msg_id.decode('UTF-8')), 0)
                        # Fetch it from the server
                        status, data = mailbox.fetch(msg_id, '(RFC822)')
                        if status == "OK":
                            # Convert it to an Email object
                            msg = email.message_from_bytes(data[0][1])
                            # Get the HTML body payload
                            msg_html = extractor.fetch_payload(msg)
                            # Save the email timestamp
                            datetime_received = datetime.fromtimestamp(
                                email.utils.mktime_tz(email.utils.parsedate_tz(msg.get('date'))))
                            # Parse the message
                            msg_parsed = BeautifulSoup(msg_html, 'html.parser')
                            # Find the "View My Code" link
                            url = extractor.fetch_url(msg_parsed)
                            if url is not None:
                                urls.append([msg_id, datetime_received, url])
        if len(urls) < 1:
            self.popup.dismiss()
            return

        if browser is None:
            self.update_progress("Launching ChromeDriver...")
            chrome_options = webdriver.ChromeOptions()
            if int(config.get('Settings', 'hide_chrome_window')) == 1:
                chrome_options.add_argument("--window-position=-10000,0")

            browser = webdriver.Chrome(config.get('Settings', 'chromedriver_path'), chrome_options=chrome_options)

        for msg_id, datetime_received, url in urls:
            self.update_progress("Getting gift card from msg "+str(msg_id))
            browser.get(url)
            card = extractor.fetch_codes(browser)
            if card['card_store'] not in cards:
                cards[card['card_store']] = []

            card['datetime_received'] = str(datetime_received)
            card['url'] = url
            cards[card['card_store']].append(card)

        for store in cards:
            self.ids.csv_output.text += store + "\r\n"
            for c in cards[store]:
                self.ids.csv_output.text += "{},{},{},{},{},{}".format(
                    c['card_code'],c['card_pin'],c['card_amount'],c['card_store'],c['datetime_received'],c['url']) + "\r\n"
            self.ids.csv_output.text += "\r\n"

        browser.close()
        self.popup.dismiss()

class ExtractorGuiApp(App):
    def build_config(self, config):
        config.setdefaults('Settings', {'chromedriver_path': '', 'days': 1, 'selected_source': 'Paypal Digital Gifts', 'hide_chrome_window': 1})
        config.setdefaults('Email1', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': ''})
        config.setdefaults('Email2', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': ''})
        config.setdefaults('Email3', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': ''})
        config.setdefaults('Email4', {'imap_active': 0,'imap_host': 'imap.gmail.com','imap_port': 993,'imap_ssl': 1,'imap_username': 'username@gmail.com','imap_password': ''})

    def build_settings(self, settings):
        settings.register_type('password', SettingPassword)
        settings.add_json_panel('Settings', self.config, 'ExtractorSettings.json')
        settings.add_json_panel('Emails', self.config, 'ExtractorEmails.json')

    def dropdown_selected(self, text):
        self.window.ids.dropdownbtn.text = text
        self.config.set('Settings', 'selected_source', text)
        self.config.write()

    def build(self):
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        window = InputWindow()
        dropdown = DropDown()
        for e in extractors_list:
            btn = Button(text=e.name(), size_hint_y=None, height=30)
            btn.bind(on_release=lambda dbtn: dropdown.select(dbtn.text))
            dropdown.add_widget(btn)

        window.ids.dropdownbtn.bind(on_release=dropdown.open)
        window.ids.dropdownbtn.text = self.config.get('Settings', 'selected_source')
        dropdown.bind(on_select=lambda instance, x: self.dropdown_selected(x))

        self.window = window
        self.dropdown = dropdown

        return window

    def on_config_change(self, config, section, key, value):
        self.window.ids.dropdownbtn.bind(on_release=self.dropdown.open)
        pass


ExtractorGuiApp().run()
