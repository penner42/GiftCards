import tkinter as tk
from tkinter import StringVar, BooleanVar, Checkbutton, Button, N, E, W, S, DISABLED, ACTIVE, LEFT, TOP, INSERT
from tkinter import Text, Label
from Extract import extractors
import queue
from imaplib import IMAP4, IMAP4_SSL
from datetime import datetime, timedelta, date
from selenium import webdriver
from bs4 import BeautifulSoup
import email, threading, os
from selenium.common.exceptions import TimeoutException
from tkinter.scrolledtext import ScrolledText
import time

class ExtractFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        left_frame = tk.Frame(self)
        right_frame = tk.Frame(self)
        left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=3)
        self.progress_text = ScrolledText(right_frame)
        self.progress_text.pack(expand=1, fill="both")

        # get settings
        self._settings = self.winfo_toplevel().get_settings()
        self._queue = queue.Queue()

        all_checked = BooleanVar()
        Checkbutton(left_frame, text='Gift Card Sources', variable=all_checked,
                    command=lambda v=all_checked: self.check_all(v),
                    borderwidth=2, relief='ridge',
                    anchor=W).grid(row=1, columnspan=3, sticky=N+W+E+S)

        active_sources = self._settings['Settings']['selected_source'].split(',')
        self.checkboxes = [BooleanVar(name=extractors.extractors_list[count].name())
                           for count in range(len(extractors.extractors_list))]
        for i, c in enumerate(self.checkboxes):
            c.set(extractors.extractors_list[i].name() in active_sources)

        choices = [e.name() for e in extractors.extractors_list]
        for i, e in enumerate(extractors.extractors_list):
            Checkbutton(left_frame, text=e.name(),
                        variable=self.checkboxes[i],
                        command=lambda: self.save_sources()).grid(row=i+2, sticky=N+W)
            text = Label(left_frame, text='Only', fg='blue', cursor='hand2')
            text.bind('<Button-1>', lambda f,i=i: self.check_only(i, all_checked))
            text.grid(row=i+2, column=2)

        Button(left_frame, text='Extract',
               command=lambda: threading.Thread(target=self.extract).start()).grid(row=len(choices)+2,
                                                                                   sticky=N+W, pady=4)
        # left_frame.grid(row=0, column=0, sticky=N+W+E+S)
        # right_frame.grid(row=0, column=1, sticky=N+W+E+S)
        left_frame.pack(side=LEFT, anchor=N+W)
        right_frame.pack(side=LEFT, expand=1, fill="both")
        self.do_update()

    def save_sources(self):
        self._settings['Settings']['selected_source'] = ','.join([extractors.extractors_list[i].name()
                                                                  for i, c in enumerate(self.checkboxes) if c.get()])
        with open('giftcards.ini', 'w') as configfile:
            self._settings.write(configfile)

    def check_only(self, only, all_checked):
        for i, c in enumerate(self.checkboxes):
            c.set(i == only)
        all_checked.set(False)
        self.save_sources()

    def check_all(self, value):
        val = value.get()
        for c in self.checkboxes:
            c.set(val)
        self.save_sources()

    def do_update(self):
        try:
            while True:
                line = self._queue.get_nowait()
                self.progress_text.insert(INSERT, line+'\n')
        except queue.Empty:
            pass
        self.after(100, self.do_update)

    def save_screenshot(self, browser, card_number):
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        browser.save_screenshot(os.path.join(screenshots_dir, card_number + '.png'))

    def update_progress(self, text):
        self._queue.put_nowait(text)

    def extract(self):
        config = self._settings
        extractor = None
        self.update_progress("Initializing...")
        cards = {}
        urls = []

        e = [extractors.extractors_list[i] for i, c in enumerate(self.checkboxes) if c.get()]
        if len(e) == 0:
            self.update_progress('No sources selected!')
            return
        emails = [i for e_list in [x.email() for x in e] for i in e_list]
        # print(e[0].name())
#        e = [x for x in extractors.extractors_list if x.name() == "Gift Card Mall"]
#         if len(e) == 1:
#             extractor = e[0]
#         else:
#             # TODO: show error about no card source selected
#             return
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
                from_list = '(OR ' * (len(emails) - 1) + '(FROM "'+emails[0]+'") ' +\
                            ''.join(['(FROM "'+em+'")) ' for em in emails[1:]])[0:-1]
                # subject = ' HEADER Subject "'+extractor.subject()+'" ' if extractor.subject() is not "" else " "
                space = ' ' if len(emails) > 1 else ''
                search = '({}{}SINCE "{}")'.format(from_list, space, since)
                # status, messages = mailbox.search(None, '(OR (OR (FROM "BestBuyInfo@emailinfo.bestbuy.com") (FROM "bestbuygiftcards@cashstar.com")) (FROM "asdf@amazon.com"))')
                # search = '(FROM "gc-orders@gc.email.amazon.com") SINCE "23-Nov-2018"'
                status, messages = mailbox.search(None, search)

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
                            # Get To: and From: addresses
                            to_address = email.utils.parseaddr(msg.get("To", imap_username))[1]
                            from_address = email.utils.parseaddr(msg.get("From"))[1]
                            # Get extractor
                            extractor = [ext for ext in extractors.extractors_list if from_address in ext.email()][0]
                            # Get the HTML body payload
                            msg_html = extractor.fetch_payload(msg)
                            if msg_html is None:
                                continue
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
                                        urls.append([messages[idx], extractor,
                                                     datetime_received, u, imap_username, to_address, phonenum])
                                else:
                                    urls.append([messages[idx], extractor,
                                                 datetime_received, url, imap_username, to_address, phonenum])
        if len(urls) < 1:
            self.update_progress('No cards to extract!')
            return

        if browser is None:
            self.update_progress("Launching ChromeDriver...")
            chrome_options = webdriver.ChromeOptions()
            if int(config.get('Settings', 'hide_chrome_window')) == 1:
                chrome_options.add_argument("--window-position=-10000,0")
            browser = webdriver.Chrome(config.get('Settings', 'chromedriver_path'), chrome_options=chrome_options)
            # self.extractdialog._browser = browser

        for msg_id, extractor, datetime_received, url, imap_username, to_address, phonenum in urls:
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
                    # if page load times out, retry...
                    if 'ERR_TIMED_OUT' in browser.page_source or 'com.bhn.general.service.error' in browser.page_source:
                        self.update_progress('Page load timed out. Retrying...')
                        time.sleep(1)
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
                # if self.ids.prints.active:
                #     browser.execute_script('window.print()')
                extractor.delay()

        csv_output = ''
        for store in cards:
            # sort by time received
            cards[store] = sorted(cards[store], key=lambda k: k['datetime_received'])
            csv_output += store + "\r\n"
            for c in cards[store]:
                csv_output += "{},{},{}\r\n".format(
                    c['card_amount'], c['card_code'], c['card_pin'])
            csv_output += "\r\n"
        
        self.update_progress(csv_output)
        
        browser.close()
