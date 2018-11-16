from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from imaplib import IMAP4, IMAP4_SSL
from datetime import datetime, timedelta, date
from selenium import webdriver
from kivy.clock import mainthread
from bs4 import BeautifulSoup
from kivy.uix.dropdown import DropDown
import email
import threading
import os, sys
import tkinter as tk
from Extract.extractors import *

class ExtractDialog(BoxLayout):
    pass


class Extract(BoxLayout):
    def build(self):
        dropdown = DropDown()
        for e in extractors_list:
            btn = Button(text=e.name(), size_hint_y=None, height=30)
            btn.bind(on_release=lambda dbtn: dropdown.select(dbtn.text))
            dropdown.add_widget(btn)

        self.ids.dropdownbtn.bind(on_release=dropdown.open)
        self.ids.dropdownbtn.text = App.get_running_app().config.get('Settings', 'selected_source')
        dropdown.bind(on_select=lambda instance, x: self.dropdown_selected(x))

        self.dropdown = dropdown

    def print_checked(self, value):
        pass

    def screenshots_checked(self, value):
        c = App.get_running_app().config
        c.set('Settings', 'screenshots', 1 if value is True else 0)
        c.write()

    def label_checked(self, label):
        if label == 'screenshot':
            c = App.get_running_app().config
            value = int(c.get('Settings', 'screenshots')) ^ 1
            self.ids.screenshots.active = value == 1
            c.set('Settings', 'screenshots', value)
            c.write()
        elif label == 'print':
            self.ids.prints.active = self.ids.prints.active == False


    def selected(self):
        pass

    def dropdown_selected(self, text):
        c = App.get_running_app().config
        self.ids.dropdownbtn.text = text
        c.set('Settings', 'selected_source', text)
        c.write()

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

    def exit(self):
        sys.exit()

    @mainthread
    def update_progress(self, text, value=0):
        self.popup.children[0].children[0].children[0].children[0].children[0].text = text

    def extract_cards(self):
        extractdialog = ExtractDialog()
        self.popup = Popup(title='Extracting cards...', content=extractdialog, size_hint=(.55,.3), auto_dismiss=False)
        self.extractdialog = extractdialog
        self.popup.open()
        threading.Thread(target=self.extract_cards_real).start()

    def save_file(self):
        filename = "test.txt"
        with open(filename, "w") as text_file:
            text_file.write(self.ids.csv_output.text)

    def save_screenshot(self, browser, card_number):
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        browser.save_screenshot(os.path.join(screenshots_dir, card_number + '.png'))

    def extract_cards_real(self):
        a = App.get_running_app()
        config = a.config
        extractor = None
        self.update_progress("Initializing...", 0)
        cards = {}
        urls = []

        e = [x for x in extractors_list if x.name() == self.ids.dropdownbtn.text]
        if len(e) == 1:
            extractor = e[0]
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
                phonenum = config.get(section, 'phonenum')

                self.update_progress("Connecting to {}...".format(imap_username))

                # Connect to the server
                if imap_ssl:
                    mailbox = IMAP4_SSL(host=imap_host, port=imap_port)
                else:
                    mailbox = IMAP4(host=imap_host, port=imap_port)

                # Log in and select the configured folder
                mailbox.login(imap_username, imap_password)
                mailbox.select("INBOX")
                since = (date.today() - timedelta(days - 1)).strftime("%d-%b-%Y")
                subject = ' HEADER Subject "'+extractor.subject()+'" ' if extractor.subject() is not "" else " "
                status, messages = mailbox.search(None,'(FROM {}{}SINCE "{}")'.format(extractor.email(),
                                                                               subject,
                                                                               since))

                if status == "OK":
                    # Convert the result list to an array of message IDs
                    messages = messages[0].split()
                    for msg_id in messages:
                        self.update_progress("{}:\n     Processing message id {}...".format(imap_username, msg_id.decode('ascii')), 0)
                        # Fetch it from the server
                        status, data = mailbox.fetch(msg_id, '(RFC822)')
                        if status == "OK":
                            # Convert it to an Email object
                            msg = email.message_from_bytes(data[0][1])
                            # Get To: address for challenge completion
                            to_address = msg.get("To", imap_username)
                            # Get the HTML body payload
                            msg_html = extractor.fetch_payload(msg)
                            # Save the email timestamp
                            datetime_received = datetime.fromtimestamp(
                                email.utils.mktime_tz(email.utils.parsedate_tz(msg.get('date'))))
                            # Parse the message
                            msg_parsed = BeautifulSoup(msg_html, 'html.parser')
                            # Find the "View My Code" link
                            url = extractor.fetch_url(msg_parsed, browser, imap_username)

                            if url is not None:
                                if isinstance(url, list):
                                    for u in url:
                                        urls.append([msg_id.decode('ascii'),
                                                     datetime_received, u, imap_username, to_address, phonenum])
                                else:
                                    urls.append([msg_id.decode('ascii'),
                                                 datetime_received, url, imap_username, to_address, phonenum])
        if len(urls) < 1:
            self.popup.dismiss()
            return

        if browser is None:
            self.update_progress("Launching ChromeDriver...")
            chrome_options = webdriver.ChromeOptions()
            if int(config.get('Settings', 'hide_chrome_window')) == 1:
                chrome_options.add_argument("--window-position=-10000,0")
            browser = webdriver.Chrome(config.get('Settings', 'chromedriver_path'), chrome_options=chrome_options)
            self.extractdialog._browser = browser

        for msg_id, datetime_received, url, imap_username, to_address, phonenum in urls:
            self.update_progress("{}\n     Getting gift card from message id: {}".format(imap_username, msg_id))
            while True:
                # keep retrying to load the page if it's timing out.
                # TODO add cancel option
                while True:
                    try:
                        browser.get(url)
                    except TimeoutException:
                        continue
                    break

                # challenege for various cards
                extractor.complete_challenge(browser, to_address, phonenum)
                card = extractor.fetch_codes(browser)

                if card is None:
                    break

                if card['card_store'] not in cards:
                    cards[card['card_store']] = []

                if card['card_code'] != '':
                    break

            if card is not None:
                card['datetime_received'] = str(datetime_received)
                card['url'] = url
                cards[card['card_store']].append(card)
                if int(config.get('Settings', 'screenshots')) == 1:
                    self.save_screenshot(browser, card['card_code'])
                if self.ids.prints.active:
                    browser.execute_script('window.print()')
                extractor.delay()

        for store in cards:
            # sort by time received
            cards[store] = sorted(cards[store], key=lambda k: k['datetime_received'])
            self.children[0].ids.csv_output.text += store + "\r\n"
            for c in cards[store]:
                # self.children[0].ids.csv_output.text += "{},{},{},{},{},{}".format(
                #     c['card_code'],c['card_pin'],c['card_amount'],c['card_store'],c['datetime_received'],c['url'])+"\r\n"
                self.children[0].ids.csv_output.text += "{},{},{}\r\n".format(
                    c['card_amount'], c['card_code'], c['card_pin'])
            self.children[0].ids.csv_output.text += "\r\n"

        browser.close()
        self.extractdialog._browser = None
        self.popup.dismiss()
