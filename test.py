from tkinter import ttk
from tkinter import * 
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from Extract import extractors


def demo():
    def checked():
        print([c.get() for c in checkboxes])

    root = tk.Tk()
    root.title("ttk.Notebook")

    nb = ttk.Notebook(root)

    # adding Frames as pages for the ttk.Notebook
    # first page, which would get widgets gridded into it
    page1 = ttk.Frame(nb)
    page1.grid(column=10, row=10, sticky=(N, E, W, S))
    page1.columnconfigure(0, weight=1)
    page1.rowconfigure(0, weight=1)
    page1.pack(pady=0, padx=0)

    # Create a Tkinter variable
    tkvar = StringVar(root)

    # Dictionary with options
    checkboxes = [IntVar() for e in extractors.extractors_list]

    choices = [e.name() for e in extractors.extractors_list]
    for i, e in enumerate(extractors.extractors_list):
        Checkbutton(page1, text=e.name(), variable=checkboxes[i]).grid(row=i, sticky=W)

    tkvar.set(extractors.extractors_list[0].name())  # set the default option

    Button(page1, text='Show', command=checked).grid(row=4, sticky=W, pady=4)
    # popupMenu = OptionMenu(page1, tkvar, *choices)
    # popupMenu.grid(row=0, column=0)

    # on change dropdown value
    def change_dropdown(*args):
        print(tkvar.get())


    # link function to change dropdown
    tkvar.trace('w', change_dropdown)

    # second page
    page2 = ttk.Frame(nb)
    text = ScrolledText(page2)
    text.pack(expand=1, fill="both")

    # second page
    page3 = ttk.Frame(nb)
    text = ScrolledText(page3)
    text.pack(expand=1, fill="both")

    nb.add(page1, text='Extract')
    nb.add(page2, text='Swipe')
    nb.add(page3, text='Barcode')

    nb.pack(expand=1, fill="both")

    root.mainloop()


if __name__ == "__main__":
    demo()