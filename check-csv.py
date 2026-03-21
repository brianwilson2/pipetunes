import csv

count = 0
empty = 0

with open("tunes_clean.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        count += 1
        if not row.get("tune_name"):
            empty += 1

print("Total rows:", count)
print("Empty tune_name rows:", empty)
print("Headers:", reader.fieldnames)
