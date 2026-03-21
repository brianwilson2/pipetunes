import sqlite3
import os
import csv

DB_NAME = "tunes.db"
CSV_FILE = "tunes_clean.csv"

# ---------------------------
# DB setup
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Styles (
                     id INTEGER PRIMARY KEY,
                     style_name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Books (
                     id INTEGER PRIMARY KEY,
                     book_name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Tunes (
                     id INTEGER PRIMARY KEY,
                     name TEXT,
                     page INTEGER,
                     style_id INTEGER,
                     book_id INTEGER,
                     notes TEXT,
                     url TEXT,
                     favorite INTEGER DEFAULT 0,
                     FOREIGN KEY(style_id) REFERENCES Styles(id),
                     FOREIGN KEY(book_id) REFERENCES Books(id))''')
    conn.commit()
    conn.close()

# ---------------------------
# CSV loader
# ---------------------------
def load_csv(filename):
    if not os.path.exists(filename):
        print(f"CSV file '{filename}' not found!")
        return []

    tunes = []
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
            name = row.get("tune_name", "")
            page = row.get("page", "0")
            style = row.get("style", "")
            book = row.get("booknames", "")
            notes = row.get("notes", "")
            url = row.get("url", "")

            if not name:
                continue
            try:
                page = int(page)
            except ValueError:
                page = 0

            tunes.append({
                "name": name,
                "page": page,
                "style": style,
                "book": book,
                "notes": notes,
                "url": url
            })
    return tunes

# ---------------------------
# Insert into DB
# ---------------------------
def insert_tunes(tunes):
    if not tunes:
        print("No tunes to insert.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    added = 0
    for t in tunes:
        c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (t["style"],))
        c.execute("SELECT id FROM Styles WHERE style_name=?", (t["style"],))
        style_id = c.fetchone()[0]

        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (t["book"],))
        c.execute("SELECT id FROM Books WHERE book_name=?", (t["book"],))
        book_id = c.fetchone()[0]

        c.execute('''INSERT OR IGNORE INTO Tunes(name, page, style_id, book_id, notes, url)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (t["name"], t["page"], style_id, book_id, t["notes"], t["url"]))
        added += 1
    conn.commit()
    conn.close()
    print(f"{added} tunes inserted into {DB_NAME}.")

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    init_db()
    tunes = load_csv(CSV_FILE)
    insert_tunes(tunes)