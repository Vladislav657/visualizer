import json


# poca = {'system_RSSI': ('Уровень сигнала Wi-Fi', 'децибелл от уровня 1 мВт (дБм)'),
#         'color_tempCT': ('Цветовая температура света', 'Кельвин (К)'),
#         'soil_soilT': ('Температура почвы', 'градусов по Цельсию (°C)'),
#         'weather_temp': ('Температура воздуха', 'градусов по Цельсию (°C)'),
#         'weather_pressure': ('Атмосферное давление', 'миллиметров ртутного столба (мм.рт.ст.)'),
#         'weather_humidity': ('Относительная влажность воздуха', 'процентов (%)'),
#         'light_lux': ('Освещённость', 'люкс (лк)'),
#         'light_blink': ('Коэффициент пульсации (Процент мерцания)', 'процентов (%)')}
#
# klop = {'T': ('Температура воздуха', 'градусов по Цельсию (°C)'),
#         'P': ('Атмосферное давление', 'миллиметров ртутного столба (мм.рт.ст.)'),
#         'H': ('Относительная влажность воздуха', 'процентов (%)')}
#
#
# utils_for_monitoring = {'Роса-К-1': poca,
#                         'РОСА К-2': poca,
#                         'КЛОП-МН': klop,
#                         'Hydra-L': {
#                             'system_RSSI': ('Уровень сигнала Wi-Fi', 'децибелл от уровня 1 мВт (дБм)'),
#                             'BME280_temp': ('Температура воздуха', 'градусов по Цельсию (°C)'),
#                             'BME280_pressure': ('Атмосферное давление', 'миллиметров ртутного столба (мм.рт.ст.)'),
#                             'BME280_humidity': ('Относительная влажность воздуха', 'процентов (%)')
#                         },
#                         'КЛОП-МНУ': klop,
#                         }
#'Свежесть-19B', 'Опорный барометр', 'Паскаль', 'Тест Студии'

# fields = {}
#
# with open(f'data.json', encoding='UTF-8') as f:
#     data = json.load(f)
#     for key in data:
#         if data[key]['uName'] not in fields.keys():
#             fields[data[key]['uName']] = {}
#
#         for field in data[key]['data'].keys():
#             if field not in fields[data[key]['uName']].keys():
#                 fields[data[key]['uName']][field] = data[key]['data'][field]
#
# for field in fields:
#     print('\n\n', field, sep='', end='')
#     for f in fields[field]:
#         print('\n\t', (f, fields[field][f]), sep='', end='')


def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


print(is_digit(''))

# i: int = 0
# for key in data.keys():
#     print(data[key])
#     i += 1
#     if i == 50:
#         break
# print('\n\n\n')
#
# utils = {}
# for key in data.keys():
#     if data[key]['uName'] not in utils_for_monitoring:
#         continue
#     if data[key]['uName'] not in utils:
#         utils[data[key]['uName']] = []
#     for field in data[key]['data'].keys():
#         if field not in utils[data[key]['uName']]:
#             utils[data[key]['uName']].append(field)
#
# for key in utils.keys():
#     print(key, ':', end=' ')
#     print(utils[key])
