from tkinter import *
from tkinter.ttk import *
import threading


class EntryWithHintText(Entry):
    def __init__(self, master=None, hint='Hint Text', hint_color='grey', **args):
        s = Style()
        self.style_name = str(id(self)) + 'EntryWithHintText.TEntry'
        s.configure(self.style_name, foreground=hint_color, selectborderwidth=0,
                    selectforeground=hint_color,
                    selectbackground=s.lookup(self.style_name, 'fieldbackground'))
        self.text = StringVar()
        self.modified = False
        super().__init__(master, style=self.style_name, textvariable=self.text, **args)
        self.hint = hint
        self.put_hint()
        self.bind('<Visibility>', self.visible)
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<Button-1>", self.check_cursor)
        self.bind("<ButtonRelease-1>", self.check_cursor)
        self.bind("<B1-Motion>", self.check_cursor)
        self.bind("<Left>", self.check_cursor)
        self.bind("<Right>", self.check_cursor)
        self.text.trace('w', self.entry_changed)

    def check_cursor(self, *args):
        if not self.modified:
            self.selection_range(0, 0)
            threading.Thread(target=lambda: self.icursor(0)).start()

    def put_hint(self):
        self.modified = False
        self.configure(style=self.style_name)
        self.delete(0, END)
        self.insert(0, self.hint)
        self.selection_range(0, 0)
        threading.Thread(target=lambda: self.icursor(0)).start()

    def visible(self, *args):
        self.selection_range(0, 0)
        if not self.modified:
            threading.Thread(target=lambda: self.icursor(0)).start()

    def entry_changed(self, *args):
        if not self.modified:
            # if the user tried to delete something from the hint, fail
            if len(self.text.get()) < len(self.hint):
                self.put_hint()
            else:
                text = self.text.get()[self.index(INSERT)-1]
                self.configure(style='TEntry')
                self.delete(0, END)
                self.insert(INSERT, text)
                self.modified = True
        else:
            if not self.text.get():
                self.put_hint()

    def foc_in(self, *args):
        if not self.modified:
            self.selection_range(0, 0)
            threading.Thread(target=lambda: self.icursor(0)).start()
