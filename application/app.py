import csv
import json

from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk

from .utils import get_json_data, get_csv_data


class App:
    def __init__(self):
        self.root = Tk()
        self.create_window()

        self.toolbar = Frame(self.root, borderwidth=1)
        self.create_toolbar()

        self.way_to_load_data = Frame(self.toolbar, relief=SOLID)
        self.way_to_load_data.grid(row=0, column=0)

        self.way = StringVar(value='file')
        self.load_from_file = ttk.Radiobutton(self.way_to_load_data, text='Загрузить данные с файла', value='file',
                                              variable=self.way, command=self.way_selected)
        self.load_from_file.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.load_from_server = ttk.Radiobutton(self.way_to_load_data, text='Загрузить данные с сервера',
                                                value='server', variable=self.way, command=self.way_selected)
        self.load_from_server.pack(anchor=NW, fill=X, padx=5, pady=5)

        # -------------------------------------------------------------------------

        self.open_file_frame = Frame(self.toolbar, relief=SOLID)
        self.filetype_var = StringVar(value='JSON')
        self.choose_filetype_combobox = ttk.Combobox(self.open_file_frame, textvariable=self.filetype_var,
                                                     values=['JSON', 'CSV'], state='readonly')
        self.open_file_button = ttk.Button(master=self.open_file_frame, text='Открыть файл', command=self.open_file)

        self.filename_label = ttk.Label(self.toolbar, text='Здесь отобразится путь к файлу')

        self.device_label = ttk.Label(self.toolbar)

        self.choose_device_combobox = ttk.Combobox(self.toolbar, state='readonly')

        self.choose_serials = Frame(self.toolbar, relief=SOLID)
        self.serials_label = ttk.Label(self.choose_serials, text="Серийные номера:")
        self.serials_checkbutton = []

        self.fields_listbox = Listbox(selectmode=MULTIPLE)

        self.chosen_fields = Frame(self.toolbar, relief=SOLID)
        self.fields_label = ttk.Label(master=self.chosen_fields, text="Поля для обработки:")
        self.fields_list = []

        self.load_from_file_tools()

    def load_from_file_tools(self):
        self.open_file_frame.grid(row=0, column=1)
        self.choose_filetype_combobox.pack(anchor=NW, fill=X, padx=5, pady=5)
        self.open_file_button.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.filename_label.configure(text='Здесь отобразится путь к файлу')
        self.filename_label.grid(row=0, column=2, columnspan=2)

    def load_from_server_tools(self):
        self.open_file_frame.grid_forget()
        self.choose_filetype_combobox.pack_forget()
        self.open_file_button.pack_forget()

        self.filename_label.grid_forget()

        self.device_label.grid_forget()
        self.choose_device_combobox.grid_forget()

        self.choose_serials.grid_forget()
        self.serials_label.pack_forget()
        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()
        self.serials_checkbutton.clear()

        self.fields_listbox.grid_forget()

        self.chosen_fields.grid_forget()
        self.fields_label.pack_forget()

    def way_selected(self):
        if self.way.get() == 'file':
            self.load_from_file_tools()
        elif self.way.get() == 'server':
            self.load_from_server_tools()

    def create_window(self):
        self.root.geometry('700x600+300+100')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')

    def create_toolbar(self):
        for c in range(4):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)
        self.toolbar.pack(fill=X, expand=True, padx=5, pady=5, anchor=N)

    def create_choose_device_combobox(self, dct, var):
        def device_selected(event):
            self.configure_serials(dct, var)
            self.fields_listbox.configure(listvariable=Variable(value=list(dct[var.get()]['fields'].keys())))

        self.choose_device_combobox.configure(textvariable=var, values=list(dct.keys()))
        self.choose_device_combobox.bind("<<ComboboxSelected>>", device_selected)

    def configure_serials(self, dct, var):
        def serial_selected():
            result = "Серийные номера: "
            for k in range(len(self.serials_checkbutton)):
                if self.serials_checkbutton[k][0].get() == 1:
                    result = f"{result} {self.serials_checkbutton[k][1]['text']}"
            self.serials_label.configure(text=result)

        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()

        self.serials_checkbutton.clear()
        self.serials_label.configure(text="Серийные номера:")

        serials = sorted(list(dct[var.get()]['serials'].keys()))
        for i in range(len(serials)):
            serial_var = IntVar()
            self.serials_checkbutton.append((serial_var, ttk.Checkbutton(master=self.choose_serials,
                                                                         text=serials[i],
                                                                         variable=serial_var,
                                                                         command=serial_selected)))
            self.serials_checkbutton[i][1].pack(anchor=NW, fill=X, padx=5, pady=5)

    def create_fields_listbox(self, dct, var=None):
        def field_selected(event):
            selected_indices = self.fields_listbox.curselection()
            selected_fields = ",".join([self.fields_listbox.get(i) for i in selected_indices])
            msg = f"Поля для обработки: {selected_fields}"
            self.fields_label["text"] = msg

        if var is None:
            self.fields_listbox.configure(listvariable=Variable(value=list(dct['fields'].keys())))
        else:
            self.fields_listbox.configure(listvariable=Variable(value=dct[var.get()]['fields']))
        self.fields_listbox.bind("<<ListboxSelect>>", field_selected)

    # def create_fields_list(self, dct, var):
    #     for field in dct[var.get()]['fields']: продолжить !!!

    def open_file(self):
        if self.filetype_var.get() == 'JSON':
            self.open_json_file()
        elif self.filetype_var.get() == 'CSV':
            self.open_csv_file()

    def file_not_found(self):
        self.filename_label.configure(text='Здесь отобразится путь к файлу')
        showerror(title="Ошибка", message="Файл не найден")

    def open_json_file(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        self.filename_label.configure(text=filename)

        try:
            with open(filename, encoding='UTF-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.file_not_found()
            return None

        devices_dict = get_json_data(data)

        self.device_label.grid_forget()

        if (len(list(devices_dict.keys()))) == 0:
            showerror(title="Ошибка", message="Файл пуст")
            return None

        devices_var = StringVar(value=list(devices_dict.keys())[0])

        self.choose_device_combobox.grid(row=1, column=0)

        self.choose_serials.grid(row=1, column=1)
        self.serials_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.fields_listbox.grid(row=1, column=2)

        self.chosen_fields.grid(row=1, column=3, columnspan=2)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.create_choose_device_combobox(devices_dict, devices_var)
        self.configure_serials(devices_dict, devices_var)
        self.create_fields_listbox(devices_dict, devices_var)

    def open_csv_file(self):
        filename = askopenfilename(filetypes=[('CSV files', '*.csv')])
        self.filename_label.configure(text=filename)

        try:
            with open(filename) as f:
                data = list(csv.reader(f, delimiter=';'))
        except FileNotFoundError:
            self.file_not_found()
            return None

        fields_dict = get_csv_data(data)

        self.choose_device_combobox.grid_forget()

        self.choose_serials.grid_forget()
        self.serials_label.pack_forget()
        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()
        self.serials_checkbutton.clear()

        if (len(list(fields_dict.keys()))) == 0:
            showerror(title="Ошибка", message="Файл пуст")
            return None

        self.device_label.configure(text='Прибор (серийный номер): \n' + fields_dict['device'])
        self.device_label.grid(row=1, column=0)

        self.fields_listbox.grid(row=1, column=1)

        self.chosen_fields.grid(row=1, column=2, columnspan=2)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.create_fields_listbox(fields_dict)

    def run(self):
        self.root.mainloop()
