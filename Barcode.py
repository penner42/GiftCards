from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter.ttk import *
import re


class BarcodeFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        Separator(self, orient=HORIZONTAL).grid(row=0, columnspan=4, sticky=E+W, pady=5)

        Label(self, text='PIN:').grid(row=1, column=0, sticky=W)
        self.pin_field = Entry(self, width=10)
        self.pin_field.grid(row=1, column=1, sticky=W)
        self.pin_field.bind('<Return>', self.pin_entered)

        Label(self, text='Scan Barcode:').grid(row=1, column=2)
        self.code_field = Entry(self)
        self.code_field.grid(row=1, column=3, sticky=E+W)
        self.code_field.bind('<Return>', self.code_entered)

        Separator(self, orient=HORIZONTAL).grid(row=2, columnspan=4, sticky=E+W, pady=5)

        Label(self, text='Scan Output').grid(row=3)

        self.output_text = ScrolledText(self, bg='#F0F0F0', borderwidth=2, relief=GROOVE)
        self.output_text.config(state=DISABLED)
        self.output_text.grid(row=4, columnspan=4, sticky=N+E+W+S)

    def pin_entered(self, event=None):
        if '%B' in self.pin_field.get():
            pin, code = self.pin_field.get().split('%B')
            self.detect(pin, code)
        else:
            self.code_field.focus()

    def code_entered(self, event=None):
        self.detect(self.pin_field.get(), self.code_field.get())

    def detect(self, pin, code):
        code = code.replace('%B', '')

        # kohl's. others?
        if len(code) == 30:
            code = code[-19:]
        # cabela's
        elif re.search("^\d{10}[a-zA-Z]{6}$", code):
            pin = code[-6:]
            code = code[:9]
        elif len(code) != 19 and len(code) != 16:
            self.code_field.delete(0, END)
            return

        output_line = '{},{}\n'.format(''.join(code[i:i+4] for i in range(0,len(code), 4)), pin)
        self.output_text.config(state=NORMAL)
        self.output_text.insert('end-1c', output_line)
        self.output_text.see(END)
        self.output_text.config(state=DISABLED)

        self.code_field.delete(0, END)
        self.pin_field.delete(0, END)
        self.pin_field.focus()
