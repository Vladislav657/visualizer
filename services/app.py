import json

from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk

from .utils import get_json_data


class App:
    def __init__(self):
        self.root = Tk()
        self.create_window()

        self.toolbar = Frame(self.root, borderwidth=1)
        self.create_toolbar()

        self.open_file_button = ttk.Button(master=self.toolbar, text='Открыть файл', command=self.open_json_file)
        self.open_file_button.grid(row=0, column=0)

        self.filename_label = ttk.Label(self.toolbar, text='Здесь отобразится путь к файлу')
        self.filename_label.grid(row=0, column=1)

        self.choose_device_combobox = ttk.Combobox(self.toolbar, state='readonly')
        self.choose_device_combobox.grid(row=0, column=3)

        self.choose_serials = Frame(self.toolbar, relief=SOLID)
        self.choose_serials.grid(row=1, column=0)

        self.serials_label = ttk.Label(self.choose_serials, text="Серийные номера:")
        self.serials_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.serials_listbox = Listbox(self.choose_serials, selectmode=MULTIPLE)
        self.serials_listbox.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.choose_fields = Frame(self.toolbar, relief=SOLID)
        self.choose_fields.grid(row=1, column=1)

        self.fields_label = ttk.Label(master=self.choose_fields, text="Поля для обработки:")
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.fields_listbox = Listbox(master=self.choose_fields, selectmode=MULTIPLE)
        self.fields_listbox.pack(anchor=NW, fill=X, padx=5, pady=5)

    def create_window(self):
        self.root.geometry('700x600+300+100')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')

    def create_toolbar(self):
        for c in range(3):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)
        self.toolbar.pack(fill=X, expand=True, padx=5, pady=5, anchor=N)

    def create_choose_device_combobox(self, devices_dict, devices_var):
        def device_selected(event):
            self.serials_listbox.delete(0, END)
            for serial in sorted(list(devices_dict[devices_var.get()]['serials'].keys())):
                self.serials_listbox.insert(END, serial)

            self.fields_listbox.delete(0, END)
            for field in devices_dict[devices_var.get()]['fields']:
                self.fields_listbox.insert(END, field)

        self.choose_device_combobox.configure(textvariable=devices_var, values=list(devices_dict.keys()))
        self.choose_device_combobox.bind("<<ComboboxSelected>>", device_selected)

    def create_serials_listbox(self, devices_dict, devices_var):
        def serial_selected(event):
            selected_indices = self.serials_listbox.curselection()
            selected_serials = ",".join([self.serials_listbox.get(i) for i in selected_indices])
            msg = f"Серийные номера: {selected_serials}"
            self.serials_label["text"] = msg

        self.serials_listbox.configure(listvariable=
                                       Variable(value=sorted(list(devices_dict[devices_var.get()]['serials'].keys()))))
        self.serials_listbox.bind("<<ListboxSelect>>", serial_selected)

    def create_fields_listbox(self, devices_dict, devices_var):
        def field_selected(event):
            selected_indices = self.fields_listbox.curselection()
            selected_fields = ",".join([self.fields_listbox.get(i) for i in selected_indices])
            msg = f"Поля для обработки: {selected_fields}"
            self.fields_label["text"] = msg

        self.fields_listbox.configure(listvariable=Variable(value=devices_dict[devices_var.get()]['fields']))
        self.fields_listbox.bind("<<ListboxSelect>>", field_selected)

    def open_json_file(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        self.filename_label.configure(text=filename)

        with open(filename, encoding='UTF-8') as f:
            data = json.load(f)

        devices_dict = get_json_data(data)
        devices_var = StringVar(value=list(devices_dict.keys())[0])

        self.create_choose_device_combobox(devices_dict, devices_var)
        self.create_serials_listbox(devices_dict, devices_var)
        self.create_fields_listbox(devices_dict, devices_var)

    def run(self):
        self.root.mainloop()
