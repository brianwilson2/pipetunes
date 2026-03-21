import csv  # add this at the top with your other imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, BooleanProperty
import sqlite3
import os

print("RUNNING:", __file__)


# DB_NAME = "tunes.db"

# ---------------------------
# Setup database with sample data
# ---------------------------
import csv  # make sure this is at the top of the file

def init_db():
    conn = sqlite3.connect("/home/brian/arduino-python/pipes/tunes.db")
 #   conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tables
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
            page_number INTEGER,
            style_id INTEGER,
            book_id INTEGER,
            notes TEXT,
            favorite INTEGER DEFAULT 0,
            FOREIGN KEY(style_id) REFERENCES Styles(id),
            FOREIGN KEY(book_id) REFERENCES Books(id)
        )
    ''')

    conn.commit()

    # Now load CSV and insert into DB
    tunes = load_csv("tunes_clean.csv")

    print("Tunes loaded into memory:", len(tunes))


    # Insert styles and books
    for t in tunes:
        c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (t["style"],))
        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (t["booknames"],))

    # Insert tunes
    for t in tunes:
        c.execute("SELECT id FROM Styles WHERE style_name=?", (t["style"],))
        style_id = c.fetchone()[0]

        c.execute("SELECT id FROM Books WHERE book_name=?", (t["booknames"],))
        book_id = c.fetchone()[0]

        for i, t in enumerate(tunes):
                if i < 5:
                    print("Inserting:", t["tune_name"])

        c.execute('''
            INSERT INTO Tunes(name, page_number, style_id, book_id, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (t["tune_name"], t["page"], style_id, book_id, t["notes"]))
            

    # insert code here


    print(f"Loaded {len(tunes)} tunes into database.")

    conn.commit()
    conn.close()



def load_csv(filename):
    tunes = []

    def safe_int(value):
        try:
            return int(value.strip())
        except (ValueError, AttributeError):
            return 0

    with open(filename, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # normalize keys
            row = {k.strip().lower(): (v.strip() if v else "")
                   for k, v in row.items() if k is not None}

            name = row.get("tune_name", "")
            if not name:
                print("EMPTY NAME ROW:", row)

            tunes.append({
                "tune_name": name,
                "page": safe_int(row.get("page", 0)),
                "style": row.get("style", ""),
                "booknames": row.get("booknames", ""),
                "notes": row.get("notes", "")
            })
    print(tunes[0])

    return tunes





# ---------------------------
# UI
# ---------------------------
class TuneRow(BoxLayout):
    tune_name = StringProperty()
    details = StringProperty()
    favorite = BooleanProperty(False)
    tune_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = [5, 5, 5, 5]
        self.size_hint_y = None
        self.height = 120  # enough space for multiple lines

        # Tune name
        self.label_name = Label(
            text=f"[b]Tune:[/b] {self.tune_name}", markup=True, size_hint_y=None, height=25, halign='left', valign='middle')
        self.label_name.bind(size=self.label_name.setter('text_size'))
        self.add_widget(self.label_name)

        # Page
        self.label_page = Label(text=f"[b]Page:[/b] {self.details.split('|')[0].strip()}",
                                markup=True, size_hint_y=None, height=25, halign='left', valign='middle')
        self.label_page.bind(size=self.label_page.setter('text_size'))
        self.add_widget(self.label_page)

        # Style
        self.label_style = Label(text=f"[b]Style:[/b] {self.details.split('|')[1].strip()}",
                                 markup=True, size_hint_y=None, height=25, halign='left', valign='middle')
        self.label_style.bind(size=self.label_style.setter('text_size'))
        self.add_widget(self.label_style)

        # Book
        self.label_book = Label(text=f"[b]Book:[/b] {self.details.split('|')[2].strip()}",
                                markup=True, size_hint_y=None, height=25, halign='left', valign='middle')
        self.label_book.bind(size=self.label_book.setter('text_size'))
        self.add_widget(self.label_book)

        # Notes
        self.label_notes = Label(text=f"[b]Notes:[/b] {self.details.split('|')[3].strip()}",
                                 markup=True, size_hint_y=None, height=25, halign='left', valign='middle')
        self.label_notes.bind(size=self.label_notes.setter('text_size'))
        self.add_widget(self.label_notes)

        # Favorite button
        self.fav_btn = Button(text="★" if self.favorite else "☆",
                              size_hint_y=None, height=40, font_size=24)
        self.fav_btn.bind(on_release=self.toggle_favorite)
        self.add_widget(self.fav_btn)

    def toggle_favorite(self, instance):
        self.favorite = not self.favorite
        self.fav_btn.text = "★" if self.favorite else "☆"
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE Tunes SET favorite=? WHERE id=?",
                  (1 if self.favorite else 0, self.tune_id))
        conn.commit()
        conn.close()


class PipeTunesApp(App):
    def build(self):
        if not os.path.exists(DB_NAME):
            init_db()

        self.conn = sqlite3.connect(DB_NAME)
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search bar
        self.search_input = TextInput(
            hint_text="Search tune name...", size_hint_y=None, height=40)
        self.search_input.bind(text=self.update_results)
        self.root.add_widget(self.search_input)

        # Scrollable list
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.root.add_widget(self.scroll)

        self.update_results()
        return self.root

    def update_results(self, *args):
        self.grid.clear_widgets()
        query = self.search_input.text
        c = self.conn.cursor()
        sql = '''
            SELECT t.id, t.name, t.page_number, s.style_name, b.book_name, t.notes, t.favorite
            FROM Tunes t
            JOIN Styles s ON t.style_id = s.id
            JOIN Books b ON t.book_id = b.id
            WHERE t.name LIKE ?
            ORDER BY t.name
        '''
        c.execute(sql, (f"%{query}%",))
        for row in c.fetchall():
            t_id, name, page, style, book, notes, fav = row
            details = f"{page} | {style} | {book} | {notes}"
            tune_row = TuneRow(
                tune_name=name, details=details, favorite=bool(fav))
            tune_row.tune_id = t_id
            self.grid.add_widget(tune_row)

    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    PipeTunesApp().run()
