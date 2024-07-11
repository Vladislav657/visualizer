def is_digit(string: str) -> bool:
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def get_data_keys(data: dict) -> dict:
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

        for field in fields.keys():
            if field not in devices[name][serial].keys():
                devices[name][serial][field] = []
            devices[name][serial][field].append(fields[field])

    return devices
