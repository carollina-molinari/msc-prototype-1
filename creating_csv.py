import csv

header = ['name_sample']
def header_names(variable, lower, upper):
    i = 0
    for i in range(lower,upper):
        seq = str(variable)+str(i)
        header.append(seq)
        seq = []

header_names("C", 0, 256)
header_names("R", 0, 256)
header_names("G", 0, 256)
header_names("B", 0, 256)
header_names("H", 0, 180)
header_names("S", 0, 256)
header_names("V", 0, 256)
   

with open('wine_samples_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(header)


