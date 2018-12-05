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
        Label(edit_frame, text='Enabled: ').grid(row=0, column=0, sticky=E)
        self.email_enabled_variable = BooleanVar()
        self.email_enabled_checkbox = Checkbutton(edit_frame, state=DISABLED, variable=self.email_enabled_variable)
        self.email_enabled_checkbox.grid(row=0, column=1, sticky=W)
        Label(edit_frame, text='Email Address: ').grid(row=1, column=0, sticky=E)
        self.email_address_entry = Entry(edit_frame, text='', width=30, state=DISABLED)
        self.email_address_entry.grid(row=1, column=1)
        Label(edit_frame, text='Username: ').grid(row=2, column=0, sticky=E)
        self.username_entry = Entry(edit_frame, text='', width=30, state=DISABLED)
        self.username_entry.grid(row=2, column=1)
        Label(edit_frame, text='Password: ').grid(row=2, column=2, sticky=E)
        self.password_entry = Entry(edit_frame, show='*', text='', width=20, state=DISABLED)
        self.password_entry.grid(row=2, column=3)
        Label(edit_frame, text='IMAP Host: ').grid(row=3, column=0, sticky=E)
        self.imap_host_entry = Entry(edit_frame, text='', width=30, state=DISABLED)
        self.imap_host_entry.grid(row=3, column=1, sticky=W)
        Label(edit_frame, text='IMAP Port: ').grid(row=3, column=2, sticky=E)
        self.imap_port_entry = Entry(edit_frame, text='', width=10, state=DISABLED)
        self.imap_port_entry.grid(row=3, column=3, sticky=W)
        Label(edit_frame, text='SSL Enabled: ').grid(row=4, column=0, sticky=E)
        self.ssl_enabled_variable = BooleanVar()
        self.ssl_enabled_checkbox = Checkbutton(edit_frame, state=DISABLED, variable=self.ssl_enabled_variable)
        self.ssl_enabled_checkbox.grid(row=4, column=1, sticky=W)
        Label(edit_frame, text='Phone number: ').grid(row=4, column=2, sticky=E)
        self.phone_number_entry = Entry(edit_frame, text='', width=15, state=DISABLED)
        self.phone_number_entry.grid(row=4, column=3, sticky=W)
        Label(edit_frame,
              text='Note: Phone number is used for gift card retrieval challenges from some sources.').grid(
            row=5, column=0, columnspan=10, sticky=W)

        button_frame = Frame(edit_frame)
        button_frame.grid(row=6, sticky=S+E, columnspan=10, padx=3, pady=3)
        self.revert_button = Button(button_frame, text='Revert', state=DISABLED, command=self.revert_email)
        self.revert_button.grid(row=0, column=0)
        self.save_button = Button(button_frame, text='Save', state=DISABLED, command=self.save_email)
        self.save_button.grid(row=0, column=1)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        Label(top_frame, text='ChromeDriver Executable: ').grid(row=0, column=0, pady=5, padx=5, sticky=W)
        self.chromedriver_filename = EntryWithHintText(top_frame,hint='Path to ChromeDriver executable.')
        self.chromedriver_filename.grid(row=0, column=1, sticky=E+W)
        Button(top_frame, text='Select', command=self.choose_file).grid(row=0, column=3, padx=5)

        self.email_fields = [(self.email_address_entry, 'email_address'),
                             (self.username_entry, 'imap_username'),
                             (self.password_entry, 'imap_password'),
                             (self.imap_host_entry, 'imap_host'),
                             (self.imap_port_entry, 'imap_port'),
                             (self.phone_number_entry, 'phonenum')
                             ]

        self.load_settings()

    def choose_file(self):
        filename = askopenfilename(title='Select chromedriver.exe', filetypes=[("", "*.exe")])
        if filename != '':
            self.chromedriver_filename.set(filename)

    def revert_email(self):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        section = 'Email'+str(selected+1)
        self.email_copy[selected] = dict(self._settings[section])
        self.email_clicked(None)

    def save_email(self):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        print('save '+str(selected))

    def load_settings(self):
        self.chromedriver_filename.set(self._settings.get('Settings', 'chromedriver_path'))
        self.email_list.delete(0, END)
        for email in (e for e in self._settings.sections() if e.startswith('Email')):
            section = self._settings[email]
            section.setdefault('imap_username', 'username@gmail.com')
            section.setdefault('email_address', section['imap_username'])
            section.setdefault('imap_active', 'True')
            section.setdefault('imap_host', 'imap.gmail.com')
            section.setdefault('imap_port', '993')
            section.setdefault('imap_ssl', 'True')
            section.setdefault('imap_password', '')
            section.setdefault('phonenum', '')

            self.email_copy.append(dict(section))
            self.email_list.insert(END, section['email_address'])

    def email_clicked(self, event):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        email_copy = self.email_copy[selected]
        # enable all fields
        self.email_enabled_checkbox.configure(state=NORMAL)
        self.email_enabled_variable.set(email_copy['imap_active'])
        self.ssl_enabled_checkbox.configure(state=NORMAL)
        self.ssl_enabled_variable.set(email_copy['imap_ssl'])
        self.revert_button.configure(state=NORMAL)
        self.save_button.configure(state=NORMAL)

        for f in self.email_fields:
            f[0].configure(state=NORMAL)
            f[0].delete(0, END)
            f[0].insert(0, email_copy[f[1]])
