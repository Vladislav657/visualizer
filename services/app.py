import json

from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk

from .utils import get_data_keys


class App:
    def __init__(self):
        self.root = Tk()
        self.create_window()

        self.toolbar = None
        self.create_toolbar()

        self.open_file_button = ttk.Button(master=self.toolbar, text='Открыть файл', command=self.open_json_file)
        self.open_file_button.grid(row=0, column=0)

        self.filename_label = ttk.Label(self.toolbar, background='gray', foreground='white')
        self.filename_label.grid(row=0, column=1)

        self.choose_device_combobox = ttk.Combobox(self.toolbar, state='readonly')
        self.choose_device_combobox.grid(row=0, column=3)

        self.choose_fields = Frame(self.toolbar, bg='gray', relief=SOLID)
        self.choose_fields.grid(row=1, column=0, columnspan=2)

        self.selection_label = ttk.Label(master=self.choose_fields, text="Вы выбрали:")
        self.selection_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.fields_listbox = Listbox(master=self.choose_fields, selectmode=MULTIPLE)
        self.fields_listbox.pack(anchor=NW, fill=X, padx=5, pady=5)

    def create_window(self):
        self.root.geometry('500x500+400+150')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')
        self.root.configure(bg='gray')

    def create_toolbar(self):
        self.toolbar = Frame(self.root, bg='black', relief=SOLID, borderwidth=1)
        for c in range(3):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)
        self.toolbar.pack(fill=X, expand=True, padx=5, pady=5, anchor=N)

    def create_choose_device_combobox(self, devices_dict, devices_list, devices_var):
        def device_selected(event):
            self.fields_listbox.delete(0, END)
            for device in devices_dict[devices_var.get()]:
                self.fields_listbox.insert(END, device)

        self.choose_device_combobox.configure(textvariable=devices_var, values=devices_list)
        self.choose_device_combobox.bind("<<ComboboxSelected>>", device_selected)
        self.choose_fields.grid(row=1, column=0)

    def create_fields_listbox(self, devices_dict, devices_var):
        def field_selected(event):
            selected_indices = self.fields_listbox.curselection()
            selected_fields = ",".join([self.fields_listbox.get(i) for i in selected_indices])
            msg = f"Вы выбрали: {selected_fields}"
            self.selection_label["text"] = msg

        self.fields_listbox.configure(listvariable=Variable(value=devices_dict[devices_var.get()]))
        self.fields_listbox.bind("<<ListboxSelect>>", field_selected)

    def open_json_file(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        self.filename_label.configure(text=filename)

        with open(filename, encoding='UTF-8') as f:
            data = json.load(f)

        devices_dict = get_data_keys(data)   # переделать !!!
        devices_list = list(devices_dict.keys())
        devices_var = StringVar(value=devices_list[0])

        self.create_choose_device_combobox(devices_dict, devices_list, devices_var)
        self.create_fields_listbox(devices_dict, devices_var)

    def run(self):
        self.root.mainloop()
