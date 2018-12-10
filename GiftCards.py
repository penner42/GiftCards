from tkinter.scrolledtext import ScrolledText
from Extract import ExtractFrame
from Barcode import BarcodeFrame
from Swipe import SwipeFrame
from Settings import SettingsFrame
import configparser
from tkinter import *
from tkinter.ttk import *
import sys


class GiftCards(Tk):
    def __init__(self):
        super().__init__()

        self._path = '.'

        if getattr(sys, 'frozen', False):
            self._path = sys._MEIPASS

        self._settings = configparser.ConfigParser(allow_no_value=True)
        self._settings.setdefault('Settings',
                                   {'chromedriver_path': '', 'days': 1, 'selected_source': '',
                                    'hide_chrome_window': True, 'screenshots': False})
        self._settings.read('giftcards.ini')

        # convert 1/0 to True/False if settings file is old
        def convert_old_setting(sec, setting):
            try:
                val = int(self._settings[sec][setting]) == 1
                if val:
                    self._settings[sec][setting] = "True"
                else:
                    self._settings[sec][setting] = "False"
            except ValueError:
                pass

        convert_old_setting('Settings', 'hide_chrome_window')
        convert_old_setting('Settings', 'screenshots')
        for section in (e for e in self._settings.sections() if e.startswith('Email')):
            convert_old_setting(section, 'imap_active')
            convert_old_setting(section, 'imap_ssl')

        self.save_settings()

        self.title("GiftCards")

        self.iconbitmap(self._path+'/giftcards.ico')

        s = Style()
        s.configure('Link.TLabel', foreground='blue')
        s.configure('Extract.TButton', foreground='green', background='green')
        s.configure('Sash', sashthickness=10, sashrelief=RAISED, handlesize=100)
        s.configure('Progress.TFrame', minsize=200)
        s.configure('Disabled.TLabel', foreground='gray')

        nb = Notebook(self)

        page1 = ExtractFrame(nb)
        page2 = SwipeFrame(nb)
        page3 = BarcodeFrame(nb)
        page4 = SettingsFrame(nb)

        nb.add(page1, text='Extract')
        nb.add(page2, text='Swipe')
        nb.add(page3, text='Barcode')
        nb.add(page4, text='Settings')
        nb.grid(column=0, row=0, sticky=N+S+E+W)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def save_settings(self):
        with open('giftcards.ini', 'w') as configfile:
            self._settings.write(configfile)

    def get_settings(self):
        return self._settings


if __name__ == "__main__":
    app = GiftCards()
    app.mainloop()
