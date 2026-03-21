from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from pathlib import Path
import sqlite3
import csv
import os

# -------------------------------
# Config
# -------------------------------
DB_NAME = "tunes.db"
DEFAULT_FOLDER = str(Path.home() / "arduino-python/pipes")
LAST_FOLDER_FILE = Path.home() / ".last_csv_folder.txt"

Window.size = (1000, 600)  # Desktop size

# -------------------------------
# CSV Upload App
# -------------------------------

class CSVUploader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        # File chooser setup
        last_folder = DEFAULT_FOLDER
        if LAST_FOLDER_FILE.exists():
            last_folder_tmp = LAST_FOLDER_FILE.read_text().strip()
            if Path(last_folder_tmp).exists():
                last_folder = last_folder_tmp

        self.filechooser = FileChooserListView(path=last_folder, filters=['*.csv'])
        self.add_widget(self.filechooser)

        # Buttons
        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.add_btn = Button(text="Add to DB")
        self.replace_btn = Button(text="Replace DB")
        self.add_btn.bind(on_release=self.add_to_db)
        self.replace_btn.bind(on_release=self.replace_db)
        buttons_layout.add_widget(self.add_btn)
        buttons_layout.add_widget(self.replace_btn)
        self.add_widget(buttons_layout)

        # Log field
        self.log = TextInput(size_hint_y=0.3, readonly=True)
        self.add_widget(self.log)

    # -------------------------------
    # Logging helper
    # -------------------------------
    def add_log(self, msg):
        self.log.text += msg + "\n"
        print(msg)

    # -------------------------------
    # CSV processing
    # -------------------------------
    def load_csv(self, csv_file):
        tunes = []
        with open(csv_file, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
                name = row.get("tune_name", "")
                page = row.get("page", "0")
                style = row.get("style", "")
                book = row.get("booknames", "")
                notes = row.get("notes", "")
                if name == "":
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
                    "notes": notes
                })
        return tunes

    # -------------------------------
    # DB insertion
    # -------------------------------
    def insert_tunes(self, tunes):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        for t in tunes:
            # Styles
            c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (t["style"],))
            c.execute("SELECT id FROM Styles WHERE style_name=?", (t["style"],))
            style_id = c.fetchone()[0]

            # Books
            c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (t["book"],))
            c.execute("SELECT id FROM Books WHERE book_name=?", (t["book"],))
            book_id = c.fetchone()[0]

            # Tunes
            c.execute("""
                INSERT INTO Tunes(name, page, style_id, book_id, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (t["name"], t["page"], style_id, book_id, t["notes"]))
        conn.commit()
        conn.close()

    # -------------------------------
    # Add to existing DB
    # -------------------------------
    def add_to_db(self, instance):
        selection = self.filechooser.selection
        if not selection:
            self.add_log("No CSV selected...")
            return
        csv_file = selection[0]
        self.add_log(f"Adding CSV: {csv_file} to existing DB...")

        tunes = self.load_csv(csv_file)
        self.insert_tunes(tunes)
        self.add_log(f"Added {len(tunes)} tunes to DB.")

        # Save folder for next time
        LAST_FOLDER_FILE.write_text(str(Path(csv_file).parent))

    # -------------------------------
    # Replace DB entirely
    # -------------------------------
    def replace_db(self, instance):
        selection = self.filechooser.selection
        if not selection:
            self.add_log("No CSV selected...")
            return
        csv_file = selection[0]
        self.add_log(f"Replacing DB with CSV: {csv_file}...")

        # Remove old DB
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)

        # Recreate tables
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS Styles (
                id INTEGER PRIMARY KEY,
                style_name TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS Books (
                id INTEGER PRIMARY KEY,
                book_name TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS Tunes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                page INTEGER,
                style_id INTEGER,
                book_id INTEGER,
                notes TEXT,
                url TEXT,
                favorite INTEGER DEFAULT 0,
                FOREIGN KEY(style_id) REFERENCES Styles(id),
                FOREIGN KEY(book_id) REFERENCES Books(id)
            )
        ''')
        conn.commit()
        conn.close()

        tunes = self.load_csv(csv_file)
        self.insert_tunes(tunes)
        self.add_log(f"DB replaced with {len(tunes)} tunes.")

        # Save folder for next time
        LAST_FOLDER_FILE.write_text(str(Path(csv_file).parent))


# -------------------------------
# App class
# -------------------------------
class CSVUploaderApp(App):
    def build(self):
        return CSVUploader()


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    CSVUploaderApp().run()