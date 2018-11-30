from tkinter import *
from tkinter.ttk import *
from EntryWithHintText import EntryWithHintText
from tkinter.filedialog import askopenfilename

class SettingsFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._settings = self.winfo_toplevel().get_settings()

        top_frame = Frame(self)
        top_frame.columnconfigure(1, weight=1)
        top_frame.grid(row=0, sticky=N+E+W+S)
        bottom_frame = Frame(self)
        bottom_frame.grid(row=1, sticky=S+E, padx=10, pady=10)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        Label(top_frame, text='ChromeDriver Executable').grid(row=0, column=0, pady=5, columnspan=5, sticky=W)
        self.chromedriver_filename = EntryWithHintText(top_frame,hint='Path to ChromeDriver executable.')
        self.chromedriver_filename.grid(row=1, column=1, sticky=E+W)
        Button(top_frame, text='Choose File', command=self.choose_file).grid(row=1, column=0)

        Button(bottom_frame, text='Revert', command=self.load_settings).grid(row=0, column=0)
        Button(bottom_frame, text='Apply').grid(row=0, column=1)

        self.load_settings()

    def choose_file(self):
        filename = askopenfilename(title='Select chromedriver.exe', filetypes=[("", "*.exe")])
        if filename != '':
            self.chromedriver_filename.set(filename)

    def load_settings(self):
        self.chromedriver_filename.set(self._settings.get('Settings', 'chromedriver_path'))
