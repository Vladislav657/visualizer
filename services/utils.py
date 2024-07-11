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

        if 'data' not in devices[name]['serials'][serial].keys():
            devices[name]['serials'][serial]['data'] = {}

        for field in fields.keys():
            if not is_digit(fields[field]) or field == 'system_Serial':
                continue
            if field not in devices[name]['fields']:
                devices[name]['fields'].append(field)
            if field not in devices[name]['serials'][serial]['data'].keys():
                devices[name]['serials'][serial]['data'][field] = []
            devices[name]['serials'][serial]['data'][field].append(float(fields[field]))

    return devices
