from kivy.uix.textinput import TextInput
import tkinter as tk


class FixBrokenClipboardTextInput(TextInput):
    def __init__(self, **kwargs):
        super(FixBrokenClipboardTextInput, self).__init__(**kwargs)

    def copy(self, data=''):
        # use tkinter here because Kivy clipboard is broken
        tkwin = tk.Tk()
        tkwin.withdraw()
        tkwin.clipboard_clear()
        tkwin.clipboard_append(self.selection_text)
        tkwin.update()
        tkwin.destroy()
