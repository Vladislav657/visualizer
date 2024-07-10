import json

from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk


class App:
    def __init__(self):
        self.root = Tk()
        self.create_window()
        self.toolbar = Frame(self.root, bg='gray', relief=SOLID, borderwidth=1)
        self.create_toolbar_grid()
        self.create_filedialog()

    def create_window(self):
        self.root.geometry('500x500+400+150')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')
        self.root.configure(bg='gray')

    def create_toolbar_grid(self):
        for c in range(3):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)
        self.toolbar.pack(fill=X, expand=True, padx=5, pady=5, anchor=N)

    def open_json_file(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        filename_label = ttk.Label(self.toolbar, text=filename)
        filename_label.grid(row=0, column=1)
        with open(filename, encoding='UTF-8') as f:
            data = json.load(f)

    def create_filedialog(self):
        open_button = ttk.Button(master=self.toolbar, text='Открыть файл', command=self.open_json_file)
        open_button.grid(row=0, column=0)

    def run(self):
        self.root.mainloop()
