import sqlite3

DB_NAME = "tunes.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Track how many duplicates we remove
removed_count = 0

# 1. Get all (name, book_id) groups that have duplicates
c.execute("""
    SELECT name, book_id, COUNT(*)
    FROM Tunes
    GROUP BY name, book_id
    HAVING COUNT(*) > 1
""")
duplicate_groups = c.fetchall()

for name, book_id, count in duplicate_groups:
    # 2. Get all rows for this tune
    c.execute("""
        SELECT id, page, notes, url, favorite
        FROM Tunes
        WHERE name=? AND book_id=?
    """, (name, book_id))
    rows = c.fetchall()

    if not rows:
        # skip this group if somehow no rows exist
        continue

    # 3. Decide which row to keep (most complete)
    best_row = max(rows, key=lambda r: sum(bool(f) for f in r[1:]))  # ignore id
    best_id = best_row[0]

    # 4. Delete all other rows
    for row in rows:
        tune_id = row[0]
        if tune_id != best_id:
            c.execute("DELETE FROM Tunes WHERE id=?", (tune_id,))
            removed_count += 1

conn.commit()
conn.close()

print(f"Removed {removed_count} duplicate tune entries.")