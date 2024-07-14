import csv


with open('csv/last_export (4).csv') as f:
    data = list(csv.reader(f, delimiter=';'))

print(*data, sep='\n')
