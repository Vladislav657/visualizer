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
            fields['fields'][field].append(row[i])
    return fields


def get_min_max_date(filetype: str, device: dict, serials: list = None) -> tuple:
    min_dates = []
    max_dates = []
    if filetype == 'JSON':
        for serial in serials:
            min_dates.append(device['serials'][serial]['period'][0])
            max_dates.append(device['serials'][serial]['period'][-1])
        return min(min_dates), max(max_dates)
    elif filetype == 'CSV':
        return device['period'][0], device['period'][-1]


def get_data_for_period(data: dict, date_1: str, date_2: str, field: str) -> tuple:
    x = [date for date in data['period'] if date_1 <= date <= date_2]
    y = [value for value in data['fields'][field]]
