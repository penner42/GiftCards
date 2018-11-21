from tkinter import ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from Extract.Extract import ExtractFrame
import configparser

#
# class Extract(tk.Frame):
#     def __init__(self, parent, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#
#         # Create a Tkinter variable
#         tkvar = StringVar(parent)
#
#         # Dictionary with options
#         self.checkboxes = [IntVar() for e in extractors.extractors_list]
#
#         choices = [e.name() for e in extractors.extractors_list]
#         for i, e in enumerate(extractors.extractors_list):
#             Checkbutton(self, text=e.name(), variable=self.checkboxes[i]).grid(row=i, sticky=W)
#
#         tkvar.set(extractors.extractors_list[0].name())  # set the default option
#
#         Button(self, text='Show', command=self.checked).grid(row=len(choices), sticky=W, pady=4)
#
#         # popupMenu = OptionMenu(page1, tkvar, *choices)
#         # popupMenu.grid(row=0, column=0)
#
#         # on change dropdown value
#         def change_dropdown(*args):
#             print(tkvar.get())
#
#         # link function to change dropdown
#         tkvar.trace('w', change_dropdown)
#
#     def checked(self):
#         print([c.get() for c in self.checkboxes])


class GiftCards(tk.Tk):
    def __init__(self):
        super().__init__()
        self._settings = configparser.ConfigParser()
        self._settings.read('giftcards.ini')

        self.title("tk.Notebook")

        nb = tk.ttk.Notebook(self)
    
        page1 = ExtractFrame(nb)
    
        # second page
        page2 = tk.Frame(nb)
        text = ScrolledText(page2)
        text.pack(expand=1, fill="both")
    
        # second page
        page3 = tk.Frame(nb)
        text = ScrolledText(page3)
        text.pack(expand=1, fill="both")
    
        nb.add(page1, text='Extract')
        nb.add(page2, text='Swipe')
        nb.add(page3, text='Barcode')
    
        nb.pack(expand=1, fill="both")

    def get_settings(self):
        return self._settings


if __name__ == "__main__":
    app = GiftCards()
    app.mainloop()
