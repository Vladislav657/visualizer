import csv
import json

from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from .utils import *


class App:
    def __init__(self):
        self.data = {}

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

        self.fields_listbox_frame = Frame(self.toolbar, relief=SOLID)
        self.fields_listbox = Listbox(self.fields_listbox_frame, selectmode=MULTIPLE, exportselection=False)
        self.fields_listbox_scrollbar = ttk.Scrollbar(orient="vertical", command=self.fields_listbox.yview,
                                                        master=self.fields_listbox_frame)
        self.fields_listbox["yscrollcommand"] = self.fields_listbox_scrollbar.set

        self.chosen_fields = Frame(self.toolbar, relief=SOLID)
        self.fields_label = ttk.Label(master=self.chosen_fields, text="Поля для обработки:")
        self.fields_list = []

        self.build_graphs_button = ttk.Button(self.toolbar, text='Построить графики', command=self.build_graphs,
                                              state=DISABLED)

        self.graphs_notebook = ttk.Notebook(self.root)
        self.graphs_frames = []

        self.load_from_file_tools()

    def load_from_file_tools(self):
        self.open_file_frame.grid(row=0, column=1)
        self.choose_filetype_combobox.pack(anchor=NW, fill=X, padx=5, pady=5)
        self.open_file_button.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.filename_label.configure(text='Здесь отобразится путь к файлу')
        self.filename_label.grid(row=0, column=2)

        self.graphs_notebook.pack(fill=BOTH, expand=True)

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

        self.fields_listbox_frame.grid_forget()
        self.fields_listbox.pack_forget()
        self.fields_listbox_scrollbar.pack_forget()

        self.chosen_fields.grid_forget()
        self.fields_label.pack_forget()
        for i in range(len(self.fields_list)):
            for j in range(len(self.fields_list[i])):
                self.fields_list[i][0][j].destroy()

        self.build_graphs_button.grid_forget()

    def way_selected(self):
        if self.way.get() == 'file':
            self.load_from_file_tools()
        elif self.way.get() == 'server':
            self.load_from_server_tools()

    def create_window(self):
        self.root.geometry('800x600+300+100')
        self.root.title('Visualizer')
        self.root.iconbitmap('graph-5_icon.ico')

    def create_toolbar(self):
        for c in range(4):
            self.toolbar.columnconfigure(index=c, weight=1)
        for r in range(3):
            self.toolbar.rowconfigure(index=r, weight=1)
        self.toolbar.pack(fill=X, expand=True, padx=5, pady=5, anchor=N)

    def build_graphs(self): # ((field_frame, label, from_button, to_button, average_combobox, graph_combobox), (average_var, graph_var))
        tab_frame = Frame(self.graphs_notebook, relief=SOLID)
        graphs_canvas = Canvas(tab_frame)

        graphs_frame = Frame(tab_frame, relief=SOLID)
        graphs_frame_id = graphs_canvas.create_window((0, 0), window=graphs_frame, anchor=CENTER)

        graphs_scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=graphs_canvas.yview)
        graphs_canvas["yscrollcommand"] = graphs_scrollbar.set

        def resize_frame(event):
            graphs_canvas.itemconfig(graphs_frame_id, width=event.width)

        graphs_canvas.bind('<Configure>', resize_frame)

        tab_frame.pack(fill=BOTH)
        graphs_canvas.pack(side=LEFT, fill=BOTH, padx=50, expand=True)
        graphs_scrollbar.pack(side=RIGHT, fill=Y)

        self.graphs_frames.append((tab_frame, graphs_canvas, graphs_frame, graphs_scrollbar))

        device = self.data['var'].get() if self.data['type'] == 'JSON' else self.data['data']['device']
        self.graphs_notebook.add(tab_frame, text=device)
        self.graphs_notebook.select(tab_frame)

        selected_indices = self.fields_listbox.curselection()
        for i in selected_indices:
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            if self.data['type'] == 'JSON':
                for k in range(len(self.serials_checkbutton)):
                    if self.serials_checkbutton[k][0].get() == 1:
                        serial = self.serials_checkbutton[k][1]['text']
                        data_for_graph = self.data['data'][device]['serials'][serial]
                        date_1 = self.fields_list[i][0][2]['text']
                        date_2 = self.fields_list[i][0][3]['text']
                        field = self.data['data'][device]['fields'][i]
                        x, y = get_data_for_period(data_for_graph, date_1, date_2, field)
                        x, y = average_request(x, y, self.fields_list[i][1][0].get())
                        ax.plot(x, y, label=f"{device} ({serial})")

            elif self.data['type'] == 'CSV':
                date_1 = self.fields_list[i][0][2]['text']
                date_2 = self.fields_list[i][0][3]['text']
                field = list(self.data['data']['fields'].keys())[i]

                x, y = get_data_for_period(self.data['data'], date_1, date_2, field)
                x, y = average_request(x, y, self.fields_list[i][1][0].get())
                ax.plot(x, y, label=device)

            ax.legend()
            ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

            toolbar = NavigationToolbar2Tk(canvas, graphs_frame)
            toolbar.update()
            toolbar.pack(side=TOP, fill=BOTH, expand=True)

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
        close_button.pack(side=BOTTOM, fill=BOTH, expand=True)

        graphs_canvas.update_idletasks()
        graphs_canvas.configure(scrollregion=graphs_canvas.bbox('all'))

    def create_choose_device_combobox(self):
        def device_selected(event):
            self.configure_serials()
            self.fields_listbox.delete(0, END)
            self.fields_listbox.configure(listvariable=
                                          Variable(value=list(self.data['data'][self.data['var'].get()]['fields'])))
            self.clear_fields_list()
            self.build_graphs_button.configure(state=DISABLED)

        self.choose_device_combobox.delete(0, END)
        self.choose_device_combobox.configure(textvariable=self.data['var'], values=list(self.data['data'].keys()))
        self.choose_device_combobox.bind("<<ComboboxSelected>>", device_selected)

    def is_serial_selected(self):
        for k in range(len(self.serials_checkbutton)):
            if self.serials_checkbutton[k][0].get() == 1:
                return True
        return False

    def configure_serials(self):
        def serial_selected():
            serials_list = []
            for k in range(len(self.serials_checkbutton)):
                if self.serials_checkbutton[k][0].get() == 1:
                    serials_list.append(self.serials_checkbutton[k][1]['text'])
            selected_indices = self.fields_listbox.curselection()
            if self.is_serial_selected():
                self.create_fields_list(self.data['data'][self.data['var'].get()],
                                        get_min_max_date('JSON',
                                                         self.data['data'][self.data['var'].get()],
                                                         serials_list))
                for f in selected_indices:
                    self.fields_list[f][0][0].pack(anchor=NW, fill=X, padx=5, pady=5)
            else:
                self.clear_fields_list()
                self.build_graphs_button.configure(state=DISABLED)

        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()

        self.serials_checkbutton.clear()

        serials = sorted(list(self.data['data'][self.data['var'].get()]['serials'].keys()))
        for i in range(len(serials)):
            serial_var = IntVar()
            self.serials_checkbutton.append((serial_var, ttk.Checkbutton(master=self.choose_serials,
                                                                         text=serials[i],
                                                                         variable=serial_var,
                                                                         command=serial_selected)))
            self.serials_checkbutton[i][1].pack(anchor=NW, fill=X, padx=5, pady=5)

    def create_fields_listbox(self):
        def field_selected(event):
            selected_indices = self.fields_listbox.curselection()
            if self.data['var'] is not None:
                if not self.is_serial_selected():
                    self.fields_listbox.select_clear(0, END)
                    showerror(title="Ошибка", message="Выберите серийные номера")
                    return None
            if self.data['var'] is None:
                self.create_fields_list(self.data['data'], get_min_max_date('CSV', self.data['data']))
            for i in range(len(self.fields_list)):
                self.fields_list[i][0][0].pack_forget()
            for i in selected_indices:
                self.fields_list[i][0][0].pack(anchor=NW, fill=X, padx=5, pady=5)
            if len(selected_indices) > 0:
                self.build_graphs_button.configure(state=NORMAL)
            elif len(selected_indices) == 0:
                self.build_graphs_button.configure(state=DISABLED)

        self.fields_listbox.delete(0, END)
        if self.data['var'] is None:
            self.fields_listbox.configure(listvariable=Variable(value=list(self.data['data']['fields'].keys())))
        else:
            self.fields_listbox.configure(listvariable=Variable(value=
                                                                self.data['data'][self.data['var'].get()]['fields']))
        self.fields_listbox.bind("<<ListboxSelect>>", field_selected)

    def create_fields_list(self, dct, dates):
        average_list = ["как есть", "усреднить за час", "усреднить за 3 часа", "усреднить за сутки", "min за сутки",
                        "max за сутки"]
        graph_list = ["линейный", "столбчатый", "точечный"]
        for i in range(len(self.fields_list)):
            for j in range(len(self.fields_list[i])):
                self.fields_list[i][0][j].destroy()

        self.fields_list.clear()

        for field in dct['fields']:
            field_frame = Frame(self.chosen_fields)

            label = ttk.Label(field_frame, text=field)
            label.pack(side=LEFT, padx=5, pady=5)

            from_button = ttk.Button(field_frame, text=dates[0])
            from_button.pack(side=LEFT, padx=5, pady=5)

            to = ttk.Label(field_frame, text='по')
            to.pack(side=LEFT, padx=5, pady=5)

            to_button = ttk.Button(field_frame, text=dates[1])
            to_button.pack(side=LEFT, padx=5, pady=5)

            average_var = StringVar(value=average_list[0])
            average_combobox = ttk.Combobox(field_frame, values=average_list, textvariable=average_var,
                                            state='readonly')
            average_combobox.pack(side=LEFT, padx=5, pady=5)

            graph_var = StringVar(value=graph_list[0])
            graph_combobox = ttk.Combobox(field_frame, values=graph_list, textvariable=graph_var, state='readonly')
            graph_combobox.pack(side=LEFT, padx=5, pady=5)

            self.fields_list.append(((field_frame, label, from_button, to_button, average_combobox, graph_combobox),
                                     (average_var, graph_var)))

    def clear_fields_list(self):
        self.fields_listbox.select_clear(0, END)
        for f in range(len(self.fields_list)):
            self.fields_list[f][0][0].pack_forget()

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

        data_dict = get_json_data(data)

        if (len(list(data_dict.keys()))) == 0:
            showerror(title="Ошибка", message="Файл пуст")
            return None

        self.device_label.grid_forget()

        self.filename_label.configure(text=filename)
        self.data['data'] = data_dict
        self.data['type'] = 'JSON'
        self.data['var'] = StringVar(value=list(data_dict.keys())[0])

        self.clear_fields_list()
        self.build_graphs_button.configure(state=DISABLED)

        self.choose_device_combobox.grid(row=0, column=3)

        self.choose_serials.grid(row=1, column=0)
        self.serials_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.fields_listbox_frame.grid(row=1, column=1)
        self.fields_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.fields_listbox_scrollbar.pack(side=RIGHT, fill=Y)

        self.chosen_fields.grid(row=1, column=2, columnspan=2)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.build_graphs_button.grid(row=2, column=0)

        self.create_choose_device_combobox()
        self.configure_serials()
        self.create_fields_listbox()

    def open_csv_file(self):
        filename = askopenfilename(filetypes=[('CSV files', '*.csv')])
        try:
            with open(filename) as f:
                data = list(csv.reader(f, delimiter=';'))
        except FileNotFoundError:
            showerror(title="Ошибка", message="Файл не загружен")
            return None

        data_dict = get_csv_data(data)

        if (len(list(data_dict.keys()))) == 0:
            showerror(title="Ошибка", message="Файл пуст")
            return None

        self.choose_device_combobox.grid_forget()
        self.choose_serials.grid_forget()
        self.serials_label.pack_forget()
        for j in range(len(self.serials_checkbutton)):
            self.serials_checkbutton[j][1].destroy()
        self.serials_checkbutton.clear()

        self.filename_label.configure(text=filename)
        self.data['data'] = data_dict
        self.data['type'] = 'CSV'
        self.data['var'] = None

        self.clear_fields_list()
        self.build_graphs_button.configure(state=DISABLED)

        self.device_label.configure(text='Прибор (серийный номер): \n' + data_dict['device'])
        self.device_label.grid(row=0, column=3)

        self.fields_listbox_frame.grid(row=1, column=0)
        self.fields_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.fields_listbox_scrollbar.pack(side=RIGHT, fill=Y)

        self.chosen_fields.grid(row=1, column=1, columnspan=2)
        self.fields_label.pack(anchor=NW, fill=X, padx=5, pady=5)

        self.build_graphs_button.grid(row=1, column=3)

        self.create_fields_listbox()

    def run(self):
        self.root.mainloop()
