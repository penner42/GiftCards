from tkinter import *
from tkinter.ttk import *
from EntryWithHintText import EntryWithHintText
from tkinter.filedialog import askopenfilename

class SettingsFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._settings = self.winfo_toplevel().get_settings()
        self.columnconfigure(1, weight=1)
        Label(self, text='ChromeDriver Executable').grid(row=0, column=0, pady=5, columnspan=5, sticky=W)
        self.chromedriver_filename = EntryWithHintText(self,hint='Path to ChromeDriver executable.')
        self.chromedriver_filename.grid(row=1, column=1, sticky=E+W)
        Button(self, text='Choose File', command=self.choose_file).grid(row=1, column=0)

    def choose_file(self):
        filename = askopenfilename(title='Select chromedriver.exe', filetypes=[("", "*.exe")])
        if filename != '':
            self.chromedriver_filename.delete(0, END)
            self.chromedriver_filename.insert(INSERT, filename)