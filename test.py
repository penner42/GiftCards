from tkinter import ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from Extract.Extract import ExtractFrame
import configparser

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
