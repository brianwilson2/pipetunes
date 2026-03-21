import csv

INPUT = "tunes_raw_1480.csv"
OUTPUT = "tunes_raw_1480_clean.csv"

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
    # read raw lines first
    raw_lines = infile.readlines()

clean_rows = []
for line in raw_lines:
    # remove trailing commas and whitespace
    line = line.rstrip().rstrip(',')
    clean_rows.append(line)

# write cleaned lines to a temp file
with open("temp_clean.csv", "w", encoding="utf-8") as temp:
    temp.write("\n".join(clean_rows))

# now read with csv module
with open("temp_clean.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    headers = [h.strip().lower() for h in reader.fieldnames]

    rows = []
    for row in reader:
        # normalize keys
        row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}

        # fix tune name
        row["tune_name"] = fix_name(row.get("tune_name", ""))

        rows.append(row)

# save clean file with correct headers
with open(OUTPUT, "w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=["tune_name", "page", "style", "booknames", "notes"])
    writer.writeheader()

    for r in rows:
        writer.writerow({
            "tune_name": r.get("tune_name", ""),
            "page": r.get("page", ""),
            "style": r.get("style", ""),
            "booknames": r.get("booknames", ""),
            "notes": r.get("notes", "")
        })

print("Cleaned CSV created:", OUTPUT)
