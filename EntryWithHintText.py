from tkinter import *
from tkinter.ttk import *
import threading


class EntryWithHintText(Entry):
    def __init__(self, master=None, hint='Hint Text', hint_color='grey', **args):
        self.trace_id = None
        self.insert_called = False

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
        self.add_trace()

    def add_trace(self):
        self.trace_id = self.text.trace('w', self.entry_changed)

    def remove_trace(self):
        if self.trace_id:
            self.text.trace_vdelete('w', self.trace_id)
            self.trace_id = None

    def set(self, text):
        self.delete(0, END)
        self.insert(0, text)

    def insert(self, index, string):
        self.insert_called = True

        if not self.modified:
            self.text.set(string)
            self.insert_called = False
        else:
            super().insert(index, string)
            self.insert_called = False

    def check_cursor(self, *args):
        if not self.modified:
            self.selection_range(0, 0)
            threading.Thread(target=lambda: self.icursor(0)).start()

    def put_hint(self):
        self.modified = False
        self.configure(style=self.style_name)
        # self.delete(0, END)
        self.insert(0, self.hint)
        self.selection_range(0, 0)
        threading.Thread(target=lambda: self.icursor(0)).start()

    def visible(self, *args):
        self.selection_range(0, 0)
        if not self.modified:
            threading.Thread(target=lambda: self.icursor(0)).start()

    def entry_changed(self, *args):
        self.remove_trace()
        if not self.modified:
            # if the user tried to delete something from the hint, fail
            if len(self.text.get()) < len(self.hint) and not self.insert_called:
                self.put_hint()
            else:
                if not self.insert_called:
                    self.text.set(self.text.get()[self.index(INSERT)-1])
                    self.insert_called = False
                self.configure(style='TEntry')
                self.modified = True
        else:
            if not self.text.get():
                self.put_hint()

        self.add_trace()

    def foc_in(self, *args):
        if not self.modified:
            self.selection_range(0, 0)
            threading.Thread(target=lambda: self.icursor(0)).start()
