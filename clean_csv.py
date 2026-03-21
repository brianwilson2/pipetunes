import csv

with open("tunes_raw.csv", newline="", encoding="utf-8") as infile, \
     open("tunes_clean.csv", "w", newline="", encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        while row and row[-1] == "":
            row.pop()
        writer.writerow(row)

print("Clean CSV written to tunes_clean.csv")
