import csv

INPUT = "tunes_raw_1480.csv"
OUTPUT = "tunes_raw_1480_cleaned.csv"

def fix_name(name):
    name = name.strip()
    if name.lower().endswith(", the"):
        base = name[:-5].strip()
        return "The " + base
    if name.lower().endswith(", a"):
        base = name[:-3].strip()
        return "A " + base
    if name.lower().endswith(", an"):
        base = name[:-4].strip()
        return "An " + base
    return name

with open(INPUT, encoding="utf-8-sig") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

headers = reader.fieldnames

with open(OUTPUT, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        row["tune_name"] = fix_name(row["tune_name"])
        writer.writerow(row)

print("Done. Total rows:", len(rows))
