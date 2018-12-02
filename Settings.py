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

        middle_frame = Frame(self)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.grid(row=1, sticky=NSEW)

        Label(middle_frame, text='Email Addresses').grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        self.email_list = Listbox(middle_frame, width=50)
        self.email_list.grid(row=1)
        self.email_list.bind('<<ListboxSelect>>', self.email_clicked)
        self.email_copy = []

        Label(middle_frame, text='Selected email address').grid(row=0, column=1, columnspan=5,
                                                                padx=5, pady=5, sticky=NW)
        edit_frame = Frame(middle_frame)
        edit_frame.grid(row=1, column=1, sticky=NSEW, padx=10)
        Label(edit_frame, text='asdf').grid(column=1)
        Label(edit_frame, text='asdf').grid(column=1)
        Label(edit_frame, text='asdf').grid(column=1)
        Label(edit_frame, text='asdf').grid(column=1)

        bottom_frame = Frame(self)
        bottom_frame.grid(row=2, sticky=S+E, padx=10, pady=10)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        Label(top_frame, text='ChromeDriver Executable: ').grid(row=0, column=0, pady=5, padx=5, sticky=W)
        self.chromedriver_filename = EntryWithHintText(top_frame,hint='Path to ChromeDriver executable.')
        self.chromedriver_filename.grid(row=0, column=1, sticky=E+W)
        Button(top_frame, text='Select', command=self.choose_file).grid(row=0, column=3, padx=5)

        Button(bottom_frame, text='Revert', command=self.load_settings).grid(row=0, column=0)
        Button(bottom_frame, text='Apply').grid(row=0, column=1)

        self.load_settings()

    def choose_file(self):
        filename = askopenfilename(title='Select chromedriver.exe', filetypes=[("", "*.exe")])
        if filename != '':
            self.chromedriver_filename.set(filename)

    def load_settings(self):
        self.chromedriver_filename.set(self._settings.get('Settings', 'chromedriver_path'))
        for email in (e for e in self._settings.sections() if e.startswith('Email')):
            section = self._settings[email]
            section.setdefault('email_address','New Email')
            section.setdefault('imap_active', 'True')
            section.setdefault('imap_host', 'imap.gmail.com')
            section.setdefault('imap_port', '993')
            section.setdefault('imap_ssl', 'True')
            section.setdefault('imap_username', 'username@gmail.com')
            section.setdefault('imap_password', '')
            section.setdefault('phonenum', '')

            self.email_copy.append(dict(section))
            self.email_list.insert(END, section['email_address'])

    def email_clicked(self, event):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        print(self.email_copy[selected]['email_address'])
        # section = 'Email'+str(self.email_list.curselection()[0]+1)
        # print(self._settings[section]['email_address'])
