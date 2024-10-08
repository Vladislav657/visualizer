import csv
import json

from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

import numpy as np

from .utils import *


class App:
    def __init__(self):
        self.data = {}

        self.root = Tk()
        self.create_window()

        self.load_button = ttk.Button(master=self.root, text='Загрузить данные', command=self.load_data)
        self.load_button.pack(anchor=N, fill=X)

        self.toolbar = None
        self.graphs_notebook = ttk.Notebook(self.root)
        self.graphs_frames = []

    def dismiss_toolbar(self):
        self.toolbar.grab_release()
        self.toolbar.destroy()

    def load_data(self):
        self.toolbar = Toplevel()
        self.toolbar.title("Загрузить данные")
        self.toolbar.iconbitmap('graph-5_icon.ico')
        self.toolbar.geometry("1100x500")
        self.toolbar.protocol("WM_DELETE_WINDOW", self.dismiss_toolbar)  # перехватываем нажатие на крестик
        self.create_toolbar()
        self.toolbar.grab_set()

        self.open_file_frame = Frame(self.toolbar, relief=SOLID)
        self.filetype_var = StringVar(value='JSON')
        self.choose_filetype_combobox = ttk.Combobox(self.open_file_frame, textvariable=self.filetype_var,
                                                     values=['JSON', 'CSV'], state='readonly')
        self.open_file_button = ttk.Button(master=self.open_file_frame, text='Открыть файл', command=self.open_file)

        self.filename_label = ttk.Label(self.toolbar, text='Здесь отобразится путь к файлу')
        self.date_label = ttk.Label(self.toolbar)

        self.device_label = ttk.Label(self.toolbar)

        self.choose_device_frame = Frame(self.toolbar, relief=SOLID)
        self.choose_device_label = ttk.Label(self.choose_device_frame, text='Выберите прибор')
        self.choose_device_combobox = ttk.Combobox(self.choose_device_frame, state='readonly')

        self.choose_serials = Frame(self.toolbar, relief=SOLID)
        self.serials_label = ttk.Label(self.choose_serials, text="Выберите серийные номера")
        self.serials_checkbutton = []

        self.fields_listbox_frame = Frame(self.toolbar, relief=SOLID)
        self.fields_listbox = Listbox(self.fields_listbox_frame, width=30, selectmode=MULTIPLE, exportselection=False)
        self.fields_listbox_scrollbar = ttk.Scrollbar(orient="vertical", command=self.fields_listbox.yview,
                                                      master=self.fields_listbox_frame)
        self.fields_listbox["yscrollcommand"] = self.fields_listbox_scrollbar.set

        self.chosen_fields = Frame(self.toolbar, relief=SOLID)
        self.fields_label = ttk.Label(master=self.chosen_fields, text="Поля для обработки:")
        self.fields_dict = {}

        self.effective_temp_var = IntVar()
        self.effective_temp_checkbutton = ttk.Checkbutton(master=self.toolbar, text='Добавить эффективную температуру '
                                                                                    'в список полей',
                                                          variable=self.effective_temp_var,
                                                          command=self.effective_temp_selected, state=DISABLED)
        self.build_graphs_button = ttk.Button(self.toolbar, text='Построить графики', command=self.build_graphs,
                                              state=DISABLED)
        self.load_from_file_tools()

    def load_from_file_tools(self):
        self.open_file_frame.grid(row=0, column=0)
        self.choose_filetype_combobox.pack(anchor=NW, fill=X, padx=5, pady=5)
        self.open_file_button.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.filename_label.grid(row=0, column=1)

        self.graphs_notebook.pack(fill=BOTH, expand=True)

        if len(list(self.data.keys())) > 0:
            if self.data['var'] is not None:
                self.map_json_file_tools()
            else:
                self.map_csv_file_tools()

    def create_window(self):
        self.root.geometry('800x600+300+100')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')

    def create_toolbar(self):
        for c in range(4):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)

    def build_graphs(self):
        tab_frame = Frame(self.graphs_notebook, relief=SOLID)
        graphs_canvas = Canvas(tab_frame)

        graphs_frame = Frame(tab_frame, relief=SOLID)
        graphs_frame_id = graphs_canvas.create_window((0, 0), window=graphs_frame, anchor=CENTER)

        graphs_scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=graphs_canvas.yview)
        graphs_canvas["yscrollcommand"] = graphs_scrollbar.set

        def resize_frame(event):
            graphs_canvas.itemconfig(graphs_frame_id, width=event.width)

        graphs_canvas.bind('<Configure>', resize_frame)

        tab_frame.pack(side=TOP, anchor=N, fill=BOTH)
        graphs_canvas.pack(side=LEFT, fill=BOTH, padx=50, expand=True)
        graphs_scrollbar.pack(side=RIGHT, fill=Y)

        def close_graphs():
            index = self.graphs_frames.index((tab_frame, graphs_canvas, graphs_frame, graphs_scrollbar))
            self.graphs_notebook.forget(index)
            del self.graphs_frames[index]
            for child in graphs_frame.winfo_children():
                child.destroy()
            tab_frame.destroy()
            graphs_canvas.destroy()
            graphs_frame.destroy()
            graphs_scrollbar.destroy()
            close_button.destroy()

        close_button = ttk.Button(graphs_frame, text='Удалить вкладку', command=close_graphs)

        self.graphs_frames.append((tab_frame, graphs_canvas, graphs_frame, graphs_scrollbar))
        serials = None
        if self.data['var'] is not None:
            device = self.data['var'].get()
            serials = self.get_serials()
            self.graphs_notebook.add(tab_frame, text=f"{device} ({', '.join(serials)})")
        else:
            device = self.data['data']['device']
            self.graphs_notebook.add(tab_frame, text=device)

        self.graphs_notebook.select(tab_frame)

        selected_indices = self.fields_listbox.curselection()
        for i in selected_indices:
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            def set_effective_temp(x_list, y_min, y_max):
                if '_effective_temp' in field:
                    alpha = 0.3
                    font = 15
                    x_min = min(x_list)
                    if -30 <= y_min <= -24 or -30 <= y_max <= -24 or y_min <= -30 <= -24 <= y_max:
                        ax.fill_between(x_list, -30, -24, color='#00008B', alpha=alpha)
                        ax.text(x_min, -27, 'Крайне холодно', color='#191970', fontsize=font)
                    if -24 <= y_min <= -12 or -24 <= y_max <= -12 or y_min <= -24 <= -12 <= y_max:
                        ax.fill_between(x_list, -24, -12, color='#0000FF', alpha=alpha)
                        ax.text(x_min, -18, 'Очень холодно', color='#0000CD', fontsize=font)
                    if -12 <= y_min <= 0 or -12 <= y_max <= 0 or y_min <= -12 <= 0 <= y_max:
                        ax.fill_between(x_list, -12, 0, color='#00BFFF', alpha=alpha)
                        ax.text(x_min, -6, 'Холодно', color='#1E90FF', fontsize=font)
                    if 0 <= y_min <= 6 or 0 <= y_max <= 6 or y_min <= 0 <= 6 <= y_max:
                        ax.fill_between(x_list, 0, 6, color='#00FA9A', alpha=alpha)
                        ax.text(x_min, 3, 'Умеренно', color='#00FF7F', fontsize=font)
                    if 6 <= y_min <= 12 or 6 <= y_max <= 12 or y_min <= 6 <= 12 <= y_max:
                        ax.fill_between(x_list, 6, 12, color='#00FF00', alpha=alpha)
                        ax.text(x_min, 9, 'Прохладно', color='#32CD32', fontsize=font)
                    if 12 <= y_min <= 18 or 12 <= y_max <= 18 or y_min <= 12 <= 18 <= y_max:
                        ax.fill_between(x_list, 12, 18, color='#FFFF00', alpha=alpha)
                        ax.text(x_min, 15, 'Умеренно тепло', color='#FFD700', fontsize=font)
                    if 18 <= y_min <= 24 or 18 <= y_max <= 24 or y_min <= 18 <= 24 <= y_max:
                        ax.fill_between(x_list, 18, 24, color='#FF8C00', alpha=alpha)
                        ax.text(x_min, 21, 'Тепло', color='#FF7F50', fontsize=font)
                    if 24 <= y_min <= 30 or 24 <= y_max <= 30 or y_min <= 24 <= 30 <= y_max:
                        ax.fill_between(x_list, 24, 30, color='#FF4500', alpha=alpha)
                        ax.text(x_min, 27, 'Жарко', color='#B22222', fontsize=font)
                    if 30 <= y_max:
                        ax.fill_between(x_list, 30, y_max + 5, color='#FF0000', alpha=alpha)
                        ax.text(x_min, 33, 'Очень жарко', color='#8B0000', fontsize=font)

            field = self.fields_listbox.get(i)
            date_1 = self.fields_dict[field][0][2].get()
            date_2 = self.fields_dict[field][0][3].get()
            if not is_valid_date(date_1.strip()) or not is_valid_date(date_2.strip()):
                showerror('Ошибка', message='Не валидная дата')
                close_graphs()
                return None
            elif date_1 > date_2:
                showerror('Ошибка', message='Начальная дата не может быть позднее конечной')
                close_graphs()
                return None
            else:
                device_dict = self.data['data'][device] if self.data['var'] is not None else self.data['data']
                dates = get_min_max_date(device_dict, serials)
                if date_1 < dates[0] or date_2 > dates[1]:
                    showerror('Ошибка', message='Выход за диапазон дат')
                    close_graphs()
                    return None

            average = self.fields_dict[field][1][0].get()
            graph_type = self.fields_dict[field][1][1].get()
            x_min_list = []
            x_max_list = []
            y_min_list = []
            y_max_list = []

            if self.data['var'] is not None:
                len_serials = len(serials)
                bar_count = 0
                width = 0.3
                for serial in serials:
                    if field not in self.data['data'][device][serial]['fields'].keys():
                        continue
                    data_for_graph = self.data['data'][device][serial]
                    x, y = get_data_for_period(data_for_graph, date_1, date_2, field)
                    x, y = average_request(x, y, average)  # "линейный", "столбчатый", "точечный"
                    x_range = np.arange(len(x))
                    if len(x) == 0:
                        continue
                    if graph_type == "линейный":
                        ax.plot(x_range, y, label=f"{device} ({serial})")
                    elif graph_type == "столбчатый":
                        ax.bar(x_range - 2 * bar_count * width / len_serials, y, width, label=f"{device} ({serial})")
                        bar_count += 1
                    elif graph_type == "точечный":
                        ax.scatter(x_range, y, label=f"{device} ({serial})")
                    ax.set_xticks(x_range, x)
                    x_min_list.append(min(x_range))
                    x_max_list.append(max(x_range))
                    y_min_list.append(min(y))
                    y_max_list.append(max(y))

            else:
                x, y = get_data_for_period(self.data['data'], date_1, date_2, field)
                x, y = average_request(x, y, average)
                x_range = np.arange(len(x))
                if graph_type == "линейный":
                    ax.plot(x_range, y, label=device)
                elif graph_type == "столбчатый":
                    ax.bar(x_range, y, label=device)
                elif graph_type == "точечный":
                    ax.scatter(x_range, y, label=device)
                ax.set_xticks(x_range, x)
                x_min_list.append(min(x_range))
                x_max_list.append(max(x_range))
                y_min_list.append(min(y))
                y_max_list.append(max(y))

            fig.suptitle(f"{field} с {date_1} по {date_2} ({average}, {graph_type})")
            ax.legend()
            ax.xaxis.set_major_locator(MaxNLocator(nbins=7))
            ax.set_xlabel('date_time')
            ax.set_ylabel(field)
            set_effective_temp(np.arange(min(x_min_list), max(x_max_list)), min(y_min_list), max(y_max_list))
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

            toolbar = NavigationToolbar2Tk(canvas, graphs_frame)
            toolbar.update()
            toolbar.pack(side=TOP, fill=BOTH, expand=True)

        close_button.pack(side=BOTTOM, fill=BOTH, expand=True)

        graphs_canvas.update_idletasks()
        graphs_canvas.configure(scrollregion=graphs_canvas.bbox('all'))
        self.dismiss_toolbar()

    def effective_temp_selected(self):
        if self.effective_temp_var.get() == 1:
            if self.data['var'] is not None:
                serials = self.get_serials()
                effective_temp_dict = get_effective_temp(self.data['data'][self.data['var'].get()], serials)
                for serial in effective_temp_dict.keys():
                    for field in effective_temp_dict[serial].keys():
                        if field not in self.fields_listbox.get(0, END):
                            self.fields_listbox.insert(0, field)
                        if field not in self.data['data'][self.data['var'].get()][serial]['fields'].keys():
                            self.data['data'][self.data['var'].get()][serial]['fields'][field] \
                                = effective_temp_dict[serial][field]
            else:
                effective_temp_dict = get_effective_temp(self.data['data'])
                for field in effective_temp_dict.keys():
                    self.fields_listbox.insert(0, field)
                    if field not in self.data['data']['fields'].keys():
                        self.data['data']['fields'][field] = effective_temp_dict[field]
        else:
            while '_effective_temp' in self.fields_listbox.get(0):
                self.remove_field(self.fields_listbox.get(0))
                self.fields_listbox.delete(0)
            if len(self.fields_listbox.curselection()) == 0:
                self.build_graphs_button.configure(state=DISABLED)

    def device_selected(self, event):
        self.configure_serials()
        self.fields_listbox.delete(0, END)
        self.effective_temp_checkbutton.configure(state=DISABLED)
        self.effective_temp_var.set(0)
        self.clear_fields_dict()
        self.build_graphs_button.configure(state=DISABLED)

    def create_choose_device_combobox(self):
        self.choose_device_combobox.delete(0, END)
        self.choose_device_combobox.configure(textvariable=self.data['var'], values=list(self.data['data'].keys()))
        self.choose_device_combobox.bind("<<ComboboxSelected>>", self.device_selected)

    def get_serials(self):
        serials = []
        for k in range(len(self.serials_checkbutton)):
            if self.serials_checkbutton[k][0].get() == 1:
                serials.append(self.serials_checkbutton[k][1]['text'])
        return serials

    def serial_selected(self):
        selected_fields = [self.fields_listbox.get(i) for i in self.fields_listbox.curselection()]
        self.create_fields_listbox()
        if temp_humidity_in_data(list(self.fields_listbox.get(0, END))):
            self.effective_temp_checkbutton.configure(state=NORMAL)
        else:
            self.effective_temp_checkbutton.configure(state=DISABLED)
            self.effective_temp_var.set(0)
        for i in range(self.fields_listbox.size()):
            if self.fields_listbox.get(i) in selected_fields:
                self.fields_listbox.select_set(i)
        for field in selected_fields:
            if field not in self.fields_listbox.get(0, END):
                self.remove_field(field)
        if self.fields_listbox.size() == 0 or len(self.fields_listbox.curselection()) == 0:
            self.build_graphs_button.configure(state=DISABLED)

    def configure_serials(self):
        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()
        self.serials_checkbutton.clear()

        serials = sorted(list(self.data['data'][self.data['var'].get()].keys()))
        for i in range(len(serials)):
            serial_var = IntVar()
            self.serials_checkbutton.append((serial_var, ttk.Checkbutton(master=self.choose_serials,
                                                                         text=serials[i],
                                                                         variable=serial_var,
                                                                         command=self.serial_selected)))
            self.serials_checkbutton[i][1].pack(anchor=NW, fill=X, padx=5, pady=5)

    def field_selected(self, event):
        fields = [self.fields_listbox.get(i) for i in self.fields_listbox.curselection()]

        if self.data['var'] is not None:
            serials_list = self.get_serials()
            dates = get_min_max_date(self.data['data'][self.data['var'].get()], serials_list)
        else:
            dates = get_min_max_date(self.data['data'])

        for field in fields:
            if field not in self.fields_dict.keys():
                self.add_field(field, dates)

        keys = list(self.fields_dict.keys())
        for key in keys:
            if key not in fields:
                self.remove_field(key)

        if len(fields) > 0:
            self.build_graphs_button.configure(state=NORMAL)
        else:
            self.build_graphs_button.configure(state=DISABLED)

    def create_fields_listbox(self):
        self.fields_listbox.delete(0, END)
        fields = []
        if self.data['var'] is not None:
            serials = self.get_serials()
            for serial in serials:
                fields_for_serial = self.data['data'][self.data['var'].get()][serial]['fields'].keys()
                for field in fields_for_serial:
                    if '_effective_temp' in field and self.effective_temp_var.get() == 0:
                        continue
                    if field not in fields:
                        fields.append(field)
        else:
            for field in list(self.data['data']['fields'].keys()):
                if '_effective_temp' in field and self.effective_temp_var.get() == 0:
                    continue
                if field not in fields:
                    fields.append(field)
        self.fields_listbox.configure(listvariable=Variable(value=fields))
        self.fields_listbox.bind("<<ListboxSelect>>", self.field_selected)

    def clear_fields_dict(self):
        keys = list(self.fields_dict.keys())
        for key in keys:
            for j in range(len(self.fields_dict[key][0])):
                self.fields_dict[key][0][j].destroy()
            del self.fields_dict[key]

    def remove_field(self, key):
        if key not in self.fields_dict.keys():
            return None
        for j in range(len(self.fields_dict[key][0])):
            self.fields_dict[key][0][j].destroy()
        del self.fields_dict[key]

    def add_field(self, field, dates):
        average_list = ["как есть", "усреднить за час", "усреднить за 3 часа", "усреднить за сутки", "min за сутки",
                        "max за сутки"]
        graph_list = ["линейный", "столбчатый", "точечный"]

        field_frame = Frame(self.chosen_fields)
        field_frame.pack(anchor=NW, fill=X, padx=5, pady=5)

        label = ttk.Label(field_frame, text=field, foreground='blue')
        label.pack(side=LEFT, padx=5, pady=5)

        from_label = ttk.Label(field_frame, text='с')
        from_label.pack(side=LEFT, padx=5, pady=5)

        from_date = DateEntry(master=field_frame, date_pattern="yyyy-mm-dd")
        from_date.delete(0, END)
        from_date.insert(END, dates[0])
        from_date.pack(side=LEFT, padx=5, pady=5)

        to_label = ttk.Label(field_frame, text='по')
        to_label.pack(side=LEFT, padx=5, pady=5)

        to_date = DateEntry(master=field_frame, date_pattern="yyyy-mm-dd")
        to_date.delete(0, END)
        to_date.insert(END, dates[1])
        to_date.pack(side=LEFT, padx=5, pady=5)

        average_var = StringVar(value=average_list[0])
        average_combobox = ttk.Combobox(field_frame, values=average_list, textvariable=average_var,
                                        state='readonly')
        average_combobox.pack(side=LEFT, padx=5, pady=5)

        graph_var = StringVar(value=graph_list[0])
        graph_combobox = ttk.Combobox(field_frame, values=graph_list, textvariable=graph_var, state='readonly')
        graph_combobox.pack(side=LEFT, padx=5, pady=5)

        self.fields_dict[field] = ((field_frame, label, from_date, to_date, average_combobox, graph_combobox),
                                   (average_var, graph_var))

    def open_file(self):
        if self.filetype_var.get() == 'JSON':
            self.open_json_file()
        elif self.filetype_var.get() == 'CSV':
            self.open_csv_file()

    def open_json_file(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        try:
            with open(filename, encoding='UTF-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            showerror(title="Ошибка", message="Файл не загружен")
            return None

        if not is_valid_json(data):
            showerror(title="Ошибка", message="Не валидный файл")
            return None

        data_dict = get_json_data(data)

        self.device_label.grid_forget()

        self.data['data'] = data_dict
        self.data['name'] = filename
        self.data['var'] = StringVar(value=list(data_dict.keys())[0])
        self.data['first_date'] = data[list(data.keys())[0]]['Date']
        self.data['last_date'] = data[list(data.keys())[-1]]['Date']

        self.clear_fields_dict()
        self.fields_listbox.delete(0, END)
        self.build_graphs_button.configure(state=DISABLED)
        self.effective_temp_var.set(0)
        self.map_json_file_tools()

    def open_csv_file(self):
        filename = askopenfilename(filetypes=[('CSV files', '*.csv')])
        try:
            with open(filename) as f:
                data = list(csv.reader(f, delimiter=';'))
        except FileNotFoundError:
            showerror(title="Ошибка", message="Файл не загружен")
            return None

        if not is_valid_csv(data):
            showerror(title="Ошибка", message="Не валидный файл")
            return None

        data_dict = get_csv_data(data)

        self.choose_device_frame.grid_forget()
        self.choose_device_label.pack_forget()
        self.choose_device_combobox.pack_forget()

        self.choose_serials.grid_forget()
        self.serials_label.pack_forget()
        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()
        self.serials_checkbutton.clear()

        self.data['data'] = data_dict
        self.data['name'] = filename
        self.data['var'] = None
        self.data['first_date'] = data_dict['period'][0]
        self.data['last_date'] = data_dict['period'][-1]

        self.clear_fields_dict()
        self.build_graphs_button.configure(state=DISABLED)
        self.effective_temp_var.set(0)
        self.map_csv_file_tools()

    def map_json_file_tools(self):
        self.filename_label.configure(text=self.data['name'])

        self.date_label.configure(text=f"Начальная дата: {self.data['first_date']}\n"
                                       f"Конечная дата: {self.data['last_date']}")
        self.date_label.grid(row=0, column=2)

        self.choose_device_frame.grid(row=0, column=3)
        self.choose_device_label.pack(anchor=NW, fill=X, padx=5, pady=5)
        self.choose_device_combobox.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.choose_serials.grid(row=1, column=0)
        self.serials_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.fields_listbox_frame.grid(row=1, column=1)
        self.fields_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.fields_listbox_scrollbar.pack(side=RIGHT, fill=Y)

        self.chosen_fields.grid(row=1, column=2, columnspan=2)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.effective_temp_checkbutton.grid(row=2, column=0, columnspan=2)
        self.build_graphs_button.grid(row=2, column=2)

        self.create_choose_device_combobox()
        self.configure_serials()

    def map_csv_file_tools(self):
        self.filename_label.configure(text=self.data['name'])

        self.date_label.configure(text=f"Начальная дата: {self.data['first_date']}\n"
                                       f"Конечная дата: {self.data['last_date']}")
        self.date_label.grid(row=0, column=2)

        self.device_label.configure(text='Прибор (серийный номер): \n' + self.data['data']['device'])
        self.device_label.grid(row=0, column=3)

        self.fields_listbox_frame.grid(row=1, column=0)
        self.fields_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.fields_listbox_scrollbar.pack(side=RIGHT, fill=Y)

        self.chosen_fields.grid(row=1, column=1, columnspan=3)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.effective_temp_checkbutton.grid(row=2, column=0, columnspan=2)
        self.build_graphs_button.grid(row=2, column=2)

        if temp_humidity_in_data(list(self.data['data']['fields'].keys())):
            self.effective_temp_checkbutton.configure(state=NORMAL)
        else:
            self.effective_temp_checkbutton.configure(state=DISABLED)
        self.create_fields_listbox()

    def run(self):
        self.root.mainloop()
