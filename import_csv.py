# import_csv.py
import sqlite3
import csv
import os

DB_NAME = "tunes.db"

def run_import(filename):
    """Import CSV into the tunes database, skipping duplicates.
       Returns a list of skipped (name, book) tuples."""
    if not os.path.exists(filename):
        print(f"CSV file not found: {filename}")
        return []

    skipped = []

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = (row.get("tune_name") or "").strip()
            if not name:
                continue

            book = (row.get("booknames") or "").strip()
            style = (row.get("style") or "").strip()
            notes = (row.get("notes") or "").strip()
            try:
                page = int(row.get("page") or 0)
            except ValueError:
                page = 0
            try:
                url_available = int(row.get("url_available") or 0)
            except ValueError:
                url_available = 0
            try:
                favorite = int(row.get("favorite") or 0)
            except ValueError:
                favorite = 0

            # Ensure style exists
            c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (style,))
            c.execute("SELECT id FROM Styles WHERE style_name=?", (style,))
            style_id = c.fetchone()[0]

            # Ensure book exists
            c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (book,))
            c.execute("SELECT id FROM Books WHERE book_name=?", (book,))
            book_id = c.fetchone()[0]

            # Check for duplicate tune in same book
            c.execute("SELECT id FROM Tunes WHERE name=? AND book_id=?", (name, book_id))
            if c.fetchone():
                skipped.append((name, book))
                continue

            # Insert the tune
            c.execute('''
                INSERT INTO Tunes(name,page,style_id,book_id,notes,url,favorite)
                VALUES (?,?,?,?,?,?,?)
            ''', (name, page, style_id, book_id, notes, "", favorite))

    conn.commit()
    conn.close()
    return skipped