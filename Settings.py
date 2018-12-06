from tkinter import *
from tkinter.ttk import *
from EntryWithHintText import EntryWithHintText
from tkinter.filedialog import askopenfilename

class SettingsFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.modified = False
        self._settings = self.winfo_toplevel().get_settings()

        top_frame = Frame(self)
        top_frame.columnconfigure(1, weight=1)
        top_frame.grid(row=0, sticky=N+E+W+S)

        middle_frame = Frame(self)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.grid(row=1, sticky=NSEW)

        Label(middle_frame, text='Email Addresses').grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        self.email_list = Listbox(middle_frame, width=50, exportselection=0)
        self.email_list.grid(row=1)
        self.email_list.bind('<<ListboxSelect>>', self.email_clicked)
        self.email_copy = []

        Label(middle_frame, text='Selected email address').grid(row=0, column=1, columnspan=5,
                                                                padx=5, pady=5, sticky=NW)

        edit_frame = Frame(middle_frame)
        edit_frame.grid(row=1, column=1, sticky=NSEW, padx=10)
        Label(edit_frame, text='Enabled: ').grid(row=0, column=0, sticky=E)
        self.email_enabled_variable = BooleanVar()
        self.email_enabled_checkbox = Checkbutton(edit_frame, state=DISABLED,
                                                  command=self.email_enable_checked,
                                                  variable=self.email_enabled_variable)
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

        self.revert_button = Button(edit_frame, text='Revert Email', state=DISABLED, command=self.revert_email)
        self.revert_button.grid(row=6, column=0, columnspan=10, sticky=W, pady=5)

        bottom_frame = Frame(self)
        bottom_frame.grid(row=2, sticky=S+E, columnspan=10, padx=3, pady=3)
        # self.revert_button = Button(bottom_frame, text='Revert', state=DISABLED, command=self.revert_email)
        # self.revert_button.grid(row=0, column=0)
        self.save_button = Button(bottom_frame, text='Save', state=NORMAL, command=self.save_settings)
        self.save_button.grid(row=0, column=1, padx=15, pady=15)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        Label(top_frame, text='ChromeDriver Executable: ').grid(row=0, column=0, pady=5, padx=5, sticky=W)
        self.chromedriver_filename = EntryWithHintText(top_frame,hint='Path to ChromeDriver executable.')
        self.chromedriver_filename.grid(row=0, column=1, sticky=E+W)
        Button(top_frame, text='Select', command=self.choose_file).grid(row=0, column=3, padx=5)

        self.email_fields = [[self.email_address_entry, 'email_address', StringVar()],
                             [self.username_entry, 'imap_username', StringVar()],
                             [self.password_entry, 'imap_password', StringVar()],
                             [self.imap_host_entry, 'imap_host', StringVar()],
                             [self.imap_port_entry, 'imap_port', StringVar()],
                             [self.phone_number_entry, 'phonenum', StringVar()]
                             ]

        for i, f in enumerate(self.email_fields):
            f[0].configure(textvariable=f[2])
            self.email_fields[i].append(f[2].trace('w', lambda a, b, c, i=i: self.field_changed(i)))

        self.load_settings()

    def choose_file(self):
        filename = askopenfilename(title='Select chromedriver.exe', filetypes=[("", "*.exe")])
        if filename != '':
            self.chromedriver_filename.set(filename)

    def email_enable_checked(self):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        self.email_copy[selected]['modified'] = True
        self.email_copy[selected]['imap_active'] = self.email_enabled_variable.get()
        self.revert_button.configure(state=NORMAL)

    def ssl_enable_checked(self):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        self.email_copy[selected]['modified'] = True
        self.email_copy[selected]['imap_ssl'] = self.ssl_enabled_variable.get()
        self.revert_button.configure(state=NORMAL)

    def field_changed(self, i):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        self.email_copy[selected]['modified'] = True
        self.email_copy[selected][self.email_fields[i][1]] = self.email_fields[i][2].get()
        self.revert_button.configure(state=NORMAL)

    def revert_email(self):
        try:
            selected = self.email_list.curselection()[0]
        except IndexError:
            return

        section = 'Email'+str(selected+1)
        self.email_copy[selected] = dict(self._settings[section])
        self.email_copy[selected]['modified'] = False
        self.email_clicked(None)

    def save_settings(self):
        self._settings['Settings']['chromedriver_path'] = self.chromedriver_filename.get()
        for i, e in enumerate(self.email_copy):
            if e['modified']:
                section = 'Email' + str(i+1)
                self._settings[section] = dict(e)
                del self._settings[section]['modified']
                e['modified'] = False

        self.winfo_toplevel().save_settings()
        self.revert_button.configure(state=DISABLED)

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
            self.email_copy[-1]['modified'] = False
            self.email_list.insert(END, section['email_address'])

    def email_clicked(self, event):
        # disable all traces
        for f in self.email_fields:
            f[2].trace_vdelete('w', f[3])
            f[3] = None

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
        if email_copy['modified']:
            self.revert_button.configure(state=NORMAL)
        else:
            self.revert_button.configure(state=DISABLED)
#        self.save_button.configure(state=NORMAL)

        for f in self.email_fields:
            f[0].configure(state=NORMAL)
            f[2].set(email_copy[f[1]])

        # re-enable traces
        for i, f in enumerate(self.email_fields):
            f[3] = f[2].trace('w', lambda a, b, c, i=i: self.field_changed(i))

