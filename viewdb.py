import sqlite3
conn = sqlite3.connect("Tunes.db")
c = conn.cursor()
c.execute("PRAGMA table_info(Tunes)")
print(c.fetchall())
conn.close()
