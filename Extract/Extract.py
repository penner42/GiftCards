import tkinter as tk
from tkinter import StringVar, IntVar, Checkbutton, Button, N, E, W, S, DISABLED, ACTIVE
from tkinter import Text, Label
from Extract import extractors
import queue
from imaplib import IMAP4, IMAP4_SSL
from datetime import datetime, timedelta, date
from selenium import webdriver
from bs4 import BeautifulSoup
import email
import threading
from selenium.common.exceptions import TimeoutException


class ExtractFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # get settings
        self._settings = self.winfo_toplevel().get_settings()
        self._queue = queue.Queue()

        self.checkboxes = [IntVar() for e in extractors.extractors_list]

        choices = [e.name() for e in extractors.extractors_list]
        for i, e in enumerate(extractors.extractors_list):
            Checkbutton(self, text=e.name(), variable=self.checkboxes[i]).grid(row=i, sticky=N+W)
            text = Label(self, text='Only')
            text.grid(row=i, column=2)

        Button(self, text='Extract',
               command=lambda: threading.Thread(target=self.extract).start()).grid(row=len(choices),
                                                                                   sticky=N+W, pady=4)
        self.do_update()

    def do_update(self):
        try:
            while True:
                line = self._queue.get_nowait()
                print(line)
        except queue.Empty:
            pass
        self.after(100, self.do_update)

    def update_progress(self, text):
        self._queue.put_nowait(text)

    def extract(self):
        config = self._settings
        extractor = None
        self.update_progress("Initializing...")
        cards = {}
        urls = []

        e = [x for x in extractors.extractors_list if x.name() == "Samsung Pay"]
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
                    messages = [m.decode('ascii') for m in messages[0].split()]
                    if len(messages) == 0:
                        continue
                    self.update_progress("Fetching messages from {}...".format(imap_username))
                    data = []
                    try:
                        status, data = mailbox.fetch(','.join(messages), '(RFC822)')
                        # remove every other element of list, extract messages
                        data = [email.message_from_bytes(i[1]) for index, i in enumerate(data) if (index + 1) % 2 != 0]
                    except IMAP4.error:
                        # Can't fetch all messages at once, do them one at a time
                        for msg_id in messages:
                            self.update_progress("{}:\n     Fetching message id {}...".format(imap_username, msg_id))
                            # Fetch it from the server
                            status, m = mailbox.fetch(msg_id, '(RFC822)')
                            if status == "OK":
                                data.append(email.message_from_bytes(m[0][1]))

                    if status == "OK":
                        for idx, msg in enumerate(data):
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
                                        urls.append([messages[idx],
                                                     datetime_received, u, imap_username, to_address, phonenum])
                                else:
                                    urls.append([messages[idx],
                                                 datetime_received, url, imap_username, to_address, phonenum])
        # if len(urls) < 1:
        #     self.popup.dismiss()
        #     return

        if browser is None:
            self.update_progress("Launching ChromeDriver...")
            chrome_options = webdriver.ChromeOptions()
            if int(config.get('Settings', 'hide_chrome_window')) == 1:
                chrome_options.add_argument("--window-position=-10000,0")
            browser = webdriver.Chrome(config.get('Settings', 'chromedriver_path'), chrome_options=chrome_options)
            # self.extractdialog._browser = browser

        for msg_id, datetime_received, url, imap_username, to_address, phonenum in urls:
            self.update_progress("{}\n     Getting gift card from message id: {}".format(imap_username, msg_id))
            while True:
                # keep retrying to load the page if it's timing out.
                # TODO add cancel option
                while True:
                    try:
                        browser.get(url)
                    except TimeoutException:
                        self.update_progress('Page load timed out. Retrying...')
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
                # if int(config.get('Settings', 'screenshots')) == 1:
                #     self.save_screenshot(browser, card['card_code'])
                # if self.ids.prints.active:
                #     browser.execute_script('window.print()')
                extractor.delay()

        csv_output = ''
        for store in cards:
            # sort by time received
            cards[store] = sorted(cards[store], key=lambda k: k['datetime_received'])
            csv_output += store + "\r\n"
            for c in cards[store]:
                # csv_output.text += "{},{},{},{},{},{}".format(
                #     c['card_code'],c['card_pin'],c['card_amount'],c['card_store'],c['datetime_received'],c['url'])+"\r\n"
                csv_output += "{},{},{}\r\n".format(
                    c['card_amount'], c['card_code'], c['card_pin'])
            csv_output += "\r\n"
        
        self.update_progress(csv_output)
        
        browser.close()
