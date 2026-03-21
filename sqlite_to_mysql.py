import sqlite3
import mysql.connector
import os

# -------- CONFIG --------
# Local SQLite database
SQLITE_DB = "tunes.db"

# MySQL connection info
#mysql -h 5.77.41.157 -u eadar_brianscot -p eadar_tunes
#MYSQL_HOST = "islander.theukhost.net"
MYSQL_HOST="5.77.41.157"
MYSQL_USER = "eadar_brianscot"
MYSQL_PASSWORD = "XK3XTqJybsTekRr"
MYSQL_DB = "eadar_tunes"

# Server PDFs folder (local path where you uploaded them)
PDF_FOLDER = "/home/brian/arduino-python/pipes/downloaded"
PDF_BASE_URL = "http://www.eadar-lion.com/pipetunes/"  # Base URL for top-level PDFs

# ------------------------

# Helper: normalize names to match PDFs
def normalize_name(name):
    # lowercase, replace spaces with underscores, remove problematic characters
    return name.lower().replace(" ", "_").replace("'", "").replace(",", "")

# --- Connect to SQLite ---
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cursor = sqlite_conn.cursor()


sqlite_cursor.execute("SELECT id, name, page, style_id, book_id, notes, url, favorite, url_available FROM tunes")
tunes = sqlite_cursor.fetchall()
print(f"Found {len(tunes)} tunes in SQLite.")

# --- Connect to MySQL ---
mysql_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    autocommit=True
)
mysql_cursor = mysql_conn.cursor()

# --- Create table if not exists ---
create_table_sql = """
CREATE TABLE IF NOT EXISTS tunes (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    page INT,
    style_id INT,
    book_id INT,
    notes TEXT,
    url VARCHAR(500),
    favorite BOOLEAN,
    url_available BOOLEAN
) CHARACTER SET utf8mb4
"""
mysql_cursor.execute(create_table_sql)
print("MySQL table ensured.")

# --- Insert tunes ---
insert_sql = """
INSERT INTO tunes (id, name, page, style_id, book_id, notes, url, favorite, url_available)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
name=VALUES(name),
page=VALUES(page),
style_id=VALUES(style_id),
book_id=VALUES(book_id),
notes=VALUES(notes),
url=VALUES(url),
favorite=VALUES(favorite),
url_available=VALUES(url_available)
"""


for tune in tunes:
    mysql_cursor.execute(insert_sql, tune)
print(f"{len(tunes)} tunes inserted/updated in MySQL.")

# --- Update URLs for top-level PDFs ---
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
pdf_map = {normalize_name(os.path.splitext(f)[0]): f for f in pdf_files}

for tune_id, name, *rest in tunes:
    normalized = normalize_name(name)
    if normalized in pdf_map:
        pdf_url = PDF_BASE_URL + pdf_map[normalized]
        mysql_cursor.execute("UPDATE tunes SET url=%s WHERE id=%s", (pdf_url, tune_id))

print(f"Updated URLs for {len(pdf_map)} top-level PDFs.")

# --- Cleanup ---
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()
print("Done! MySQL database now contains all tunes with top-level PDFs linked.")