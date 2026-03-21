import sqlite3

conn = sqlite3.connect("tunes.db")
c = conn.cursor()
c.execute("SELECT t.name, t.page_number, s.style_name, b.book_name, t.notes, t.favorite FROM Tunes t JOIN Styles s ON t.style_id=s.id JOIN Books b ON t.book_id=b.id")
for row in c.fetchall():
    print(row)
conn.close()
