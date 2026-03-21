from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
import sqlite3
import os
import csv

DB_NAME = "tunes.db"
CSV_FILE = "tunes_clean.csv"

# Set a larger window size (desktop)
Window.size = (1200, 800)  # width x height

# ---------------------------
# Database functions
# ---------------------------
def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
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


def load_csv(filename):
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


def insert_tunes_into_db(tunes):
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
        c.execute('''
            INSERT INTO Tunes(name, page, style_id, book_id, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (t["name"], t["page"], style_id, book_id, t["notes"]))
    conn.commit()
    conn.close()


# ---------------------------
# UI Row
# ---------------------------
class TuneRow(BoxLayout):
    def __init__(self, app, tune_id, name, page, style, book, notes, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.tune_id = tune_id
        self.is_editing = False
        self.orientation = 'horizontal'
        self.spacing = 20
        self.padding = [5, 5, 5, 5]
        self.size_hint_y = None
        self.height = 70

        # Labels
        self.name_label = Label(text=name, size_hint_x=0.50)
        self.book_label = Label(text=book, size_hint_x=0.50)
        self.page_label = Label(text=str(page), size_hint_x=0.1)
        self.style_label = Label(text=style, size_hint_x=0.1)
        self.notes_label = Label(text=notes, size_hint_x=0.25)

        # Inputs (hidden initially)
        self.name_input = TextInput(text=name, size_hint_x=0.25, multiline=False)
        self.book_input = TextInput(text=book, size_hint_x=0.2, multiline=False)
        self.page_input = TextInput(text=str(page), size_hint_x=0.1, multiline=False)
        self.style_input = TextInput(text=style, size_hint_x=0.2, multiline=False)
        self.notes_input = TextInput(text=notes, size_hint_x=0.25, multiline=False)

        # Buttons
        self.edit_btn = Button(text="Edit", size_hint_x=0.1)
        self.edit_btn.bind(on_release=self.start_edit)

        self.save_btn = Button(text="Save", size_hint_x=0.1)
        self.save_btn.bind(on_release=self.save_edit)

        self.cancel_btn = Button(text="Cancel", size_hint_x=0.1)
        self.cancel_btn.bind(on_release=self.cancel_edit)

        # Show labels + edit initially
        self.add_widget(self.name_label)
        self.add_widget(self.book_label)
        self.add_widget(self.page_label)
        self.add_widget(self.style_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.edit_btn)

    def start_edit(self, instance):
        if self.is_editing:
            return
        self.is_editing = True
        self.clear_widgets()
        self.add_widget(self.name_input)
        self.add_widget(self.book_input)
        self.add_widget(self.page_input)
        self.add_widget(self.style_input)
        self.add_widget(self.notes_input)
        self.add_widget(self.save_btn)
        self.add_widget(self.cancel_btn)

    def save_edit(self, instance):
        new_name = self.name_input.text.strip()
        try:
            new_page = int(self.page_input.text.strip())
        except ValueError:
            new_page = 0
        new_style = self.style_input.text.strip()
        new_book = self.book_input.text.strip()
        new_notes = self.notes_input.text.strip()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Ensure style exists
        c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (new_style,))
        c.execute("SELECT id FROM Styles WHERE style_name=?", (new_style,))
        style_id = c.fetchone()[0]

        # Ensure book exists
        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (new_book,))
        c.execute("SELECT id FROM Books WHERE book_name=?", (new_book,))
        book_id = c.fetchone()[0]

        # Update tune
        c.execute('''
            UPDATE Tunes SET name=?, page=?, style_id=?, book_id=?, notes=? WHERE id=?
        ''', (new_name, new_page, style_id, book_id, new_notes, self.tune_id))
        conn.commit()
        conn.close()

        # Update labels and revert to view mode
        self.name_label.text = new_name
        self.book_label.text = new_book
        self.page_label.text = str(new_page)
        self.style_label.text = new_style

        self.notes_label.text = new_notes
        self.end_edit()

    def cancel_edit(self, instance):
        self.end_edit()

    def end_edit(self):
        self.clear_widgets()
        self.add_widget(self.name_label)
        self.add_widget(self.book_label)
        self.add_widget(self.page_label)
        self.add_widget(self.style_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.edit_btn)
        self.is_editing = False


# ---------------------------
# Main App
# ---------------------------
class PipeTunesApp(App):
    def build(self):
        init_db()
        tunes = load_csv(CSV_FILE)
        insert_tunes_into_db(tunes)

        self.conn = sqlite3.connect(DB_NAME)

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search field
        self.search_input = TextInput(hint_text="Search tune...", size_hint_y=None, height=40)
        self.search_input.bind(text=self.update_results)
        root.add_widget(self.search_input)

        # Scrollable results
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        # Add New Tune button
        add_btn = Button(text="Add New Tune", size_hint_y=None, height=40)
        add_btn.bind(on_release=self.add_tune)
        root.add_widget(add_btn)

        self.update_results()
        return root

    def add_tune(self, instance):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO Tunes(name, page, book_id, style_id, notes, url) VALUES (?, ?, ?, ?, ?, ?)",
                ("New Tune", 0, None, None, "", ""))
        tune_id = c.lastrowid
        conn.commit()
        conn.close()

        # Add the new row to the grid
        tune_row = TuneRow(self, tune_id, "New Tune", 0, "", "", "", "")
        self.grid.add_widget(tune_row)


    def update_results(self, *args):
        self.grid.clear_widgets()
        query = self.search_input.text.strip().lower()
        if len(query) < 1:
            return

        c = self.conn.cursor()
        c.execute('''
            SELECT t.id, t.name, t.page, s.style_name, b.book_name, t.notes
            FROM Tunes t
            JOIN Styles s ON t.style_id = s.id
            JOIN Books b ON t.book_id = b.id
            WHERE LOWER(t.name) LIKE ?
            ORDER BY t.name
            LIMIT 100
        ''', (f"%{query}%",))
        for row in c.fetchall():
            t_id, name, page, style, book, notes = row
            tune_row = TuneRow(
                app=self, tune_id=t_id, name=name, page=page,
                style=style, book=book, notes=notes
            )
            self.grid.add_widget(tune_row)

    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    PipeTunesApp().run()
