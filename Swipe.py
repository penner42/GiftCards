import re
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from EntryWithHintText import EntryWithHintText

class SwipeFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        Separator(self, orient=HORIZONTAL).grid(row=0, columnspan=4, sticky=E+W, pady=5)

        # Label(self, text='Swipe Card:').grid(row=1, column=0, sticky=W)
        self.swipe_field = EntryWithHintText(self,
                                             hint="Type PIN, then swipe card. If there's no PIN, just swipe.")
        self.swipe_field.grid(row=1, column=0, sticky=E+W)
        self.swipe_field.bind('<Return>', self.card_swiped)

        Separator(self, orient=HORIZONTAL).grid(row=2, columnspan=4, sticky=E+W, pady=5)

        Label(self, text='Swipe Output').grid(row=3)

        self.output_text = ScrolledText(self, bg='#F0F0F0', borderwidth=2, relief=GROOVE)
        self.output_text.config(state=DISABLED)
        self.output_text.grid(row=4, columnspan=4, sticky=N+E+W+S)

    def card_swiped(self, event=None):
        field_data = self.swipe_field.get()
        
        # card not swiped
        if "%B" not in field_data:
            return
        else:
            pin, data = field_data.split("%B")

        if data.count('?') != 2:
            self.swipe_field.delete(0, END)
            self.swipe_field.insert(INSERT, pin)
        else:
            # card_no = self.detect(data)
            sec1, sec2, sec3 = data.split('^')
            [t1, t2, t3] = [x.strip() for x in data.split('?')]

            if len(sec1) != 19:
                card_no = sec1[0] + sec3[14:16] + sec1[6:15] + sec3[16:20]
            else:
                card_no = sec1[0:20]

            output_line = '{},{}\n'.format(''.join(card_no[i:i + 4] for i in range(0, len(card_no), 4)), pin)
            self.output_text.config(state=NORMAL)
            self.output_text.insert('end-1c', output_line)
            self.output_text.see(END)
            self.output_text.config(state=DISABLED)
            self.swipe_field.delete(0, END)
