def is_digit(string: str) -> bool:
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def get_json_data(data: dict) -> dict:
    devices = {}

    for key in data:
        name = data[key]['uName']
        date = data[key]['Date']
        serial = data[key]['serial']
        fields = data[key]['data']

        if name not in devices.keys():
            devices[name] = {}

        if 'fields' not in devices[name].keys():
            devices[name]['fields'] = []

        if 'serials' not in devices[name].keys():
            devices[name]['serials'] = {}

        if serial not in devices[name]['serials'].keys():
            devices[name]['serials'][serial] = {}

        if 'period' not in devices[name]['serials'][serial].keys():
            devices[name]['serials'][serial]['period'] = []
        devices[name]['serials'][serial]['period'].append(date)

        if 'fields' not in devices[name]['serials'][serial].keys():
            devices[name]['serials'][serial]['fields'] = {}

        for field in fields.keys():
            if not is_digit(fields[field]) or field == 'system_Serial':
                continue
            if field not in devices[name]['fields']:
                devices[name]['fields'].append(field)
            if field not in devices[name]['serials'][serial]['fields'].keys():
                devices[name]['serials'][serial]['fields'][field] = []
            devices[name]['serials'][serial]['fields'][field].append(float(fields[field]))

    return devices


def get_csv_data(data: list) -> dict:
    fields = {}

    if len(data) <= 2:
        return fields

    fields['device'] = data[0][1]

    fields['period'] = []
    for row in data[2:]:
        fields['period'].append(row[0])

    fields['fields'] = {}
    for i in range(1, len(data[1])):
        field = data[1][i]
        if not is_digit(data[2][i]):
            continue
        if field not in fields['fields'].keys():
            fields['fields'][field] = []
        for row in data[2:]:
            fields['fields'][field].append(float(row[i]))
    return fields


def get_min_max_date(filetype: str, device: dict, serials: list = None) -> tuple:
    min_dates = []
    max_dates = []
    if filetype == 'JSON':
        for serial in serials:
            min_dates.append(device['serials'][serial]['period'][0])
            max_dates.append(device['serials'][serial]['period'][-1])
        return min(min_dates)[:-9], max(max_dates)[:-9]
    elif filetype == 'CSV':
        return device['period'][0][:-9], device['period'][-1][:-9]


def get_data_for_period(data: dict, date_1: str, date_2: str, field: str) -> tuple:
    x = []
    y = []
    field_len = len(data['fields'][field])
    for i, date in enumerate(data['period']):
        if date_1 <= date[:-9] <= date_2 and i < field_len:
            x.append(date)
            y.append(data['fields'][field][i])
    return x, y


def ave(lst: list) -> float:
    return sum(lst) / len(lst)


def average_an_hour(period: list, data: list) -> tuple:
    average = {}
    for i, date in enumerate(period):
        hour = date[:-6]
        if hour not in average.keys():
            average[hour] = []
        average[hour].append(data[i])
    x = []
    y = []
    for key, val in average.items():
        x.append(key)
        y.append(ave(val))
    return x, y


def average_three_hours(period: list, data: list) -> tuple:
    average = {}
    first = period[0][:-9]
    last = period[-1][:-6]

    hour = int(period[0][-8:-6])
    i = 0
    while f"{first} {str(hour + i).rjust(2, '0')}" <= last:
        average[f"{first} {str(hour + i).rjust(2, '0')}"] = []
        i += 3

    x = list(average.keys())
    i = 0
    for j, val in enumerate(data):
        if period[i][:-6] >= x[i + 1]:
            i += 1
        average[x[i]].append(val)
    y = [ave(value) for value in average.values()]
    return x, y


def average_a_day(period: list, data: list, func: callable) -> tuple:  # 2022-11-02 00:00:00
    average = {}
    for i, date in enumerate(period):
        day = date[:-9]
        if day not in average.keys():
            average[day] = []
        average[day].append(data[i])
    x = []
    y = []
    for key, val in average.items():
        x.append(key)
        y.append(func(val))
    return x, y


def average_request(period: list, data: list, request: str) -> tuple:
    # "как есть", "усреднить за час", "усреднить за 3 часа", "усреднить за сутки", "min за сутки",
    #                         "max за сутки"
    if request == "как есть":
        return period, data
    elif request == "усреднить за час":
        return average_an_hour(period, data)
    elif request == "усреднить за 3 часа":
        return average_three_hours(period, data)
    elif request == "усреднить за сутки":
        return average_a_day(period, data, ave)
    elif request == "min за сутки":
        return average_a_day(period, data, min)
    elif request == "max за сутки":
        return average_a_day(period, data, max)
