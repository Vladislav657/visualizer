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
    fields = {}

    for key in data:
        if data[key]['uName'] not in fields.keys():
            fields[data[key]['uName']] = []

        for field in data[key]['data'].keys():
            if (field not in fields[data[key]['uName']] and is_digit(data[key]['data'][field])
                    and field != "system_Serial"):
                fields[data[key]['uName']].append(field)
    return fields
