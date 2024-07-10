import json

from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk

from .utils import get_data_keys


class App:
    def __init__(self):
        self.root = Tk()
        self.create_window()
        self.toolbar = Frame(self.root, bg='gray', relief=SOLID, borderwidth=1)
        self.create_toolbar_grid()
        self.create_filedialog()
        self.choose_fields = Frame(self.toolbar, bg='gray', relief=SOLID, borderwidth=1)

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
        filename_label = ttk.Label(self.toolbar, text=filename, background='gray', relief=SOLID)
        filename_label.grid(row=0, column=1)
        with open(filename, encoding='UTF-8') as f:
            data = json.load(f)

        devices_dict = get_data_keys(data)
        devices_list = list(devices_dict.keys())
        devices_var = StringVar(value=devices_list[0])

        choose_device_combobox = ttk.Combobox(self.toolbar, textvariable=devices_var,
                                              values=devices_list, state='readonly')
        choose_device_combobox.grid(row=0, column=3)

        def device_selected(event):
            fields_listbox.delete(0, END)
            for device in devices_dict[devices_var.get()]:
                fields_listbox.insert(END, device)

        choose_device_combobox.bind("<<ComboboxSelected>>", device_selected)
        self.choose_fields.grid(row=1, column=0, columnspan=2)

        selection_label = ttk.Label(master=self.choose_fields, text="Вы выбрали:")
        selection_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        def field_selected(event):
            selected_indices = fields_listbox.curselection()
            selected_langs = ",".join([fields_listbox.get(i) for i in selected_indices])
            msg = f"Вы выбрали: {selected_langs}"
            selection_label["text"] = msg

        fields_listbox = Listbox(master=self.choose_fields, listvariable=Variable(value=devices_dict[devices_var.get()]),
                                 selectmode=MULTIPLE)
        fields_listbox.pack(anchor=NW, fill=X, padx=5, pady=5)
        fields_listbox.bind("<<ListboxSelect>>", field_selected)

    def create_filedialog(self):
        open_button = ttk.Button(master=self.toolbar, text='Открыть файл', command=self.open_json_file)
        open_button.grid(row=0, column=0)

    def run(self):
        self.root.mainloop()
