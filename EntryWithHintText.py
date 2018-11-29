from tkinter import *
from tkinter.ttk import *
import threading

class EntryWithHintText(Entry):
    def __init__(self, master=None, placeholder="Hint Text", color='grey'):
        s = Style()
        s.configure('EntryWithHintText.TEntry', foreground=color)
        self.text = StringVar()
        self.modified = False
        super().__init__(master, style='EntryWithHintText.TEntry', textvariable=self.text)
        self.placeholder = placeholder
        self.put_placeholder()
        self.bind('<Visibility>', self.visible)
        self.bind("<FocusIn>", self.foc_in)
        self.bind_class('<<Selection>>', self.text_selected)
        self.text.trace('w', self.entry_changed)

    def put_placeholder(self):
        self.modified = False
        self.configure(style='EntryWithHintText.TEntry')
        self.delete(0, END)
        self.insert(0, self.placeholder)
        self.selection_range(0, 0)
        threading.Thread(target=lambda: self.icursor(0)).start()

    def text_selected(self):
        print('asdf')

    def visible(self, *args):
        self.selection_range(0, 0)
        if not self.modified:
            threading.Thread(target=lambda: self.icursor(0)).start()

    def entry_changed(self, *args):
        if not self.modified:
            # if the user tried to delete something from the placeholder, fail
            if len(self.text.get()) < len(self.placeholder):
                self.put_placeholder()
            else:
                text = self.text.get()[self.index(INSERT)-1]
                self.configure(style='TEntry')
                self.delete(0, END)
                self.insert(INSERT, text)
                self.modified = True
        else:
            if not self.text.get():
                self.put_placeholder()

    def foc_in(self, *args):
        if not self.modified:
            self.selection_range(0, 0)
            threading.Thread(target=lambda: self.icursor(0)).start()
