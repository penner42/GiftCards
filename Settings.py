import re
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from EntryWithHintText import EntryWithHintText

class SettingsFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._settings = self.winfo_toplevel().get_settings()

        Label(self, text='Chromedriver Executable').grid(row=0, column=0)
        test = EntryWithHintText(self, hint='asdf')
        test.insert(0, 'blah')
        test.grid()