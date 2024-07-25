import re


months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def is_leap_year(year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def is_valid_date(date):
    pattern = re.compile(r'\d{4}-\d\d-\d\d')
    if not (pattern.match(date) and len(date) == 10):
        return False
    months[2] = 29 if is_leap_year(int(date[:4])) else 28
    if 1 <= int(date[5:7]) <= 12 and 1 <= int(date[8:10]) <= months[int(date[5:7])]:
        return True
    return False


def is_digit(string: str) -> bool:
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def is_valid_record(record: tuple) -> bool:
    if not is_digit(record[0]):
        return False
    if "Date" not in record[1] or "uName" not in record[1] or "serial" not in record[1] or \
       "data" not in record[1]:
        return False
    return True


def is_valid_json(data: dict) -> bool:
    return all(map(is_valid_record, data.items()))


def is_valid_csv(data: list) -> bool:
    if len(data) <= 2 or 'Прибор: ' not in data[0] or ' Интервал: ' not in data[0] or 'Date' not in data[1]:
        return False
    return True


def get_json_data(data: dict) -> dict:
    devices = {}

    for key in data:
        name = data[key]['uName']
        date = data[key]['Date']
        serial = data[key]['serial']
        fields = data[key]['data']

        if name not in devices.keys():
            devices[name] = {}

        if serial not in devices[name].keys():
            devices[name][serial] = {}

        if 'period' not in devices[name][serial].keys():
            devices[name][serial]['period'] = []
        devices[name][serial]['period'].append(date)

        if 'fields' not in devices[name][serial].keys():
            devices[name][serial]['fields'] = {}

        for field in fields.keys():
            if not is_digit(fields[field]) or field == 'system_Serial':
                continue
            if field not in devices[name][serial]['fields'].keys():
                devices[name][serial]['fields'][field] = []
            devices[name][serial]['fields'][field].append(float(fields[field]))

    return devices


def get_csv_data(data: list) -> dict:
    fields = {'device': data[0][1], 'period': []}

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


def get_min_max_date(device: dict, serials: list = None) -> tuple:
    min_dates = []
    max_dates = []
    if serials is not None:
        for serial in serials:
            min_dates.append(device[serial]['period'][0])
            max_dates.append(device[serial]['period'][-1])
        return min(min_dates)[:-9], max(max_dates)[:-9]
    else:
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


def date_to_hours(date: str, min_year: int) -> int: # 2023-11-02 04:19:15
    months[2] = 29 if is_leap_year(int(date[:4])) else 28
    result = 0
    for year in range(min_year, int(date[:4])):
        if is_leap_year(year):
            result += 365 * 24
    for month in range(1, int(date[5:7])):
        result += months[month] * 24
    result += int(date[8:10]) * 24 + int(date[11:13])
    return result


def average_three_hours(period: list, data: list) -> tuple:
    min_year = int(period[0][:4])
    current_hours = date_to_hours(period[0][:-6], min_year)
    current_date = period[0][:-6]
    average = {current_date: []}
    for i, date in enumerate(period):
        hour = date[:-6]
        if date_to_hours(hour, min_year) - current_hours >= 3:
            average[hour] = []
            current_hours = date_to_hours(hour, min_year)
            current_date = hour
        average[current_date].append(data[i])
    x = []
    y = []
    for key, val in average.items():
        x.append(key)
        y.append(ave(val))
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


def temp_humidity_in_data(fields: list) -> bool:
    for field in fields:
        if '_temp' in field and field.replace('_temp', '_humidity') in fields:
            return True
    return False


def get_effective_temp(device: dict, serials: list = None) -> dict:
    et_dict = {}
    if serials is not None:
        for serial in serials:
            et_dict[serial] = {}
            fields = list(device[serial]['fields'].keys())
            for field in fields:
                if '_temp' in field and field.replace('_temp', '_humidity') in fields:
                    temp = device[serial]['fields'][field]
                    hum = device[serial]['fields'][field.replace('_temp', '_humidity')]
                    et_field = field.replace('_temp', '_effective_temp')
                    effective_temp = [temp[i] - 0.4 * (temp[i] - 10) * (1 - hum[i] / 100) for i in range(len(temp))]
                    et_dict[serial][et_field] = effective_temp
    else:
        fields = list(device['fields'].keys())
        for field in fields:
            if '_temp' in field and field.replace('_temp', '_humidity') in fields:
                temp = device['fields'][field]
                hum = device['fields'][field.replace('_temp', '_humidity')]
                et_field = field.replace('_temp', '_effective_temp')
                effective_temp = [temp[i] - 0.4 * (temp[i] - 10) * (1 - hum[i] / 100) for i in range(len(temp))]
                et_dict[et_field] = effective_temp
    return et_dict
