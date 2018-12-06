from extractors import *
import queue
from imaplib import IMAP4, IMAP4_SSL
from datetime import datetime, timedelta, date
from selenium import webdriver
from bs4 import BeautifulSoup
import email, threading, os
from selenium.common.exceptions import TimeoutException
from tkinter.scrolledtext import ScrolledText
import time
from tkinter import *
from tkinter.ttk import *
from configparser import NoOptionError

class ExtractFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.extract_thread = None

        left_frame = Frame(self)
        left_frame.columnconfigure(0, weight=1)

        right_pane = Frame(self)

        output_frame = Frame(right_pane, style='Progress.TFrame')
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        self.output_label = Label(output_frame, text='Card Output', anchor=W)
        self.output_label.grid(row=0, sticky=W)

        self.output_text = ScrolledText(output_frame, bg='#F0F0F0', height=10, borderwidth=2, relief=GROOVE)
        self.output_text.config(state=DISABLED)
        self.output_text.grid(row=1, sticky=N+E+W+S)
        # right_pane.add(output_frame)

        progress_frame = Frame(right_pane, style='Progress.TFrame')
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        self.progress_label = Label(progress_frame, text='Progress', anchor=W)
        self.progress_label.grid(row=0, sticky=W)

        self.progress_text = ScrolledText(progress_frame, bg='#F0F0F0', height=10, borderwidth=2, relief=GROOVE)
        self.progress_text.config(state=DISABLED)
        self.progress_text.grid(row=1, sticky=N+E+W+S)

        # right_pane.add(progress_frame)
        output_frame.pack(expand=1, fill="both")
        progress_frame.pack(expand=1, fill="both")

        # get settings
        self._settings = self.winfo_toplevel().get_settings()
        self._queue = queue.Queue()
        self._kill_queue = queue.Queue()
        self.checkbox_widgets = []
        self.all_checked = BooleanVar()
        left_frame_checkboxes = Frame(left_frame, borderwidth=2, relief='groove')
        self.checkbox_widgets.append(Checkbutton(left_frame_checkboxes, text='Gift Card Sources',
                                                 variable=self.all_checked,
                                                 command=lambda v=self.all_checked: self.check_all(v)))
        self.checkbox_widgets[-1].grid(row=0, columnspan=3, sticky=N+W+E+S)

        Separator(left_frame_checkboxes, orient=HORIZONTAL).grid(row=1, columnspan=3, sticky=EW)

        active_sources = self._settings['Settings']['selected_source'].split(',')
        self.checkboxes = [BooleanVar(name=extractors_list[count].name())
                           for count in range(len(extractors_list))]
        for i, c in enumerate(self.checkboxes):
            c.set(extractors_list[i].name() in active_sources)

        choices = [e.name() for e in extractors_list]
        self.only_links = []
        for i, e in enumerate(extractors_list):
            self.checkbox_widgets.append(Checkbutton(left_frame_checkboxes, text=e.name(),
                                                     variable=self.checkboxes[i],
                                                     command=lambda: self.save_sources()))
            self.checkbox_widgets[-1].grid(row=i+2, sticky=N+W)
            self.only_links.append(Label(left_frame_checkboxes, text='Only', style='Link.TLabel', cursor='hand2'))
            self.only_links[-1].bind('<Button-1>', lambda f,i=i: self.check_only(i, self.all_checked))
            self.only_links[-1].grid(row=i+2, column=2)

        Separator(left_frame_checkboxes, orient=HORIZONTAL).grid(row=len(extractors_list)+2, columnspan=3, sticky=EW)
        self.take_screenshots = BooleanVar()
        self.take_screenshots.set(self._settings['Settings']['screenshots'])
        self.checkbox_widgets.append(Checkbutton(left_frame_checkboxes, text='Screenshots',
                                                 variable=self.take_screenshots,
                                                 command=lambda v=self.take_screenshots: self.toggle_screenshots(v)))
        self.checkbox_widgets[-1].grid(columnspan=3, sticky=NSEW)

        left_frame_checkboxes.grid(row=0)
        self.extract_button = Button(left_frame, text='Extract', style='Extract.TButton',command=self.extract)
        self.extract_button.grid(row=1,sticky=N+E+W+S, pady=1)
        self.cancel_button = Button(left_frame, text='Cancel', command=self.cancel)
        self.cancel_button.grid(row=2,sticky=N+E+W+S)
        self.cancel_button.configure(state=DISABLED)

        left_frame.pack(side=LEFT, anchor=N+W, padx=5, pady=5)
        right_pane.pack(side=LEFT, expand=1, fill="both")
        self.do_update()

    def toggle_screenshots(self, value):
        self._settings['Settings']['screenshots'] = str(value.get())
        self.winfo_toplevel().save_settings()

    def save_sources(self):
        self._settings['Settings']['selected_source'] = ','.join([extractors_list[i].name()
                                                                  for i, c in enumerate(self.checkboxes) if c.get()])
        self.winfo_toplevel().save_settings()

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
                if line.startswith('CARDOUTPUT'):
                    line = line[10:]
                    self.output_text.configure(state=NORMAL)
                    self.output_text.delete(1.0, END)
                    self.output_text.insert(INSERT, line)
                    self.output_text.configure(state=DISABLED)
                elif line.startswith('EXTRACTIONFINISHED'):
                    self.restore_gui()
                else:
                    self.progress_text.config(state='normal')
                    self.progress_text.insert('end-1c', line+'\n')
                    self.progress_text.config(state='disabled')
                    self.progress_text.see(END)
        except queue.Empty:
            pass
        self.after(100, self.do_update)

    def save_screenshot(self, browser, card_number):
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        browser.save_screenshot(os.path.join(screenshots_dir, card_number + '.png'))

    def update_progress(self, text):
        # check kill queue to see if we should stop
        try:
            line = self._kill_queue.get_nowait()
            if self.browser:
                self.browser.close()
            self._queue.put_nowait('Extraction canceled.')
            self.extraction_cleanup()
        except queue.Empty:
            pass
        self._queue.put_nowait(text)

    def cancel(self):
        self.update_progress('Cancelling...')
        if self.extract_thread:
            self._kill_queue.put_nowait('DIE')

    def restore_gui(self):
        for c in self.checkbox_widgets:
            c.configure(state=NORMAL)

        for l in self.only_links:
            l.configure(state=NORMAL)

        self.extract_button.configure(state=NORMAL)
        self.cancel_button.configure(state=DISABLED)


    def extract(self):
        # disable GUI
        for c in self.checkbox_widgets:
            c.configure(state=DISABLED)

        for l in self.only_links:
            l.configure(state=DISABLED)

        self.extract_button.configure(state=DISABLED)
        self.cancel_button.configure(state=NORMAL)

        self.extract_thread = threading.Thread(target=self.extract_real)
        self.extract_thread.start()

    def output_cards(self, cards):
        csv_output = 'CARDOUTPUT'
        for store in cards:
            # sort by time received
            cards[store] = sorted(cards[store], key=lambda k: k['datetime_received'])
            csv_output += store + "\r\n"
            for c in cards[store]:
                csv_output += "{},{},{}\r\n".format(
                    c['card_amount'], c['card_code'], c['card_pin'])
            csv_output += "\r\n"

        self.update_progress(csv_output)

    def extract_real(self):
        config = self._settings
        extractor = None
        self.update_progress("Initializing...")
        cards = {}
        urls = []

        e = [extractors_list[i] for i, c in enumerate(self.checkboxes) if c.get()]
        if len(e) == 0:
            self.update_progress('No sources selected!')
            self.extraction_cleanup()

        emails = [i for e_list in [x.email() for x in e] for i in e_list]
        days = int(config.get('Settings', 'days'))
        browser = None
        self.browser = None
        for section in (e for e in self._settings.sections() if e.startswith('Email')):
#        for section in ['Email1', 'Email2', 'Email3', 'Email4']:
            if config.get(section, 'imap_active') == "True":
                imap_ssl = config.get(section, 'imap_ssl') == "True"
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
                            self.update_progress("{}: Fetching message id {}...".format(imap_username, msg_id))
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
                            extractor = [ext for ext in extractors_list if from_address in ext.email()][0]
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
            self.extraction_cleanup()

        if browser is None:
            self.update_progress("Launching ChromeDriver...")
            chrome_options = webdriver.ChromeOptions()
            if config.get('Settings', 'hide_chrome_window') == 'True':
                chrome_options.add_argument("--window-position=-10000,0")
            try:
                profile = config.get('Settings', 'profile')
                chrome_options.add_argument('--user-data-dir={}'.format(profile))
            except NoOptionError:
                pass

            browser = webdriver.Chrome(config.get('Settings', 'chromedriver_path'), chrome_options=chrome_options)
            self.browser = browser # TODO make it all self.browser

        for msg_id, extractor, datetime_received, url, imap_username, to_address, phonenum in urls:
            self.update_progress("{}: Getting gift card from message id: {}".format(imap_username, msg_id))
            while True:
                # keep retrying to load the page if it's timing out.
                # TODO add cancel option
                while True:
                    try:
                        browser.get('about:blank')
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
                if config.get('Settings', 'screenshots'):
                    self.save_screenshot(browser, card['card_code'])
                # if self.ids.prints.active:
                #     browser.execute_script('window.print()')
                extractor.delay()

                # update output window for each new card
                self.output_cards(cards)

        browser.close()
        self.extraction_cleanup()

    def extraction_cleanup(self):
        self._queue.put_nowait('EXTRACTIONFINISHED')
        exit()
