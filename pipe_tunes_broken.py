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

# Set a larger window size (desktop)
Window.size = (1200, 800)  # width x height

DB_NAME = "tunes.db"
CSV_FILE = "tunes_clean.csv"


# ---------------------------
# Database functions
# ---------------------------
def init_db():
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
    def __init__(self, app, tune_id, name="", book="", page=0, style="", notes="", url="", **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.tune_id = tune_id
        self.is_editing = False
        self.orientation = 'horizontal'
        self.spacing = 10
        self.padding = [5, 5, 5, 5]
        self.size_hint_y = None
        self.height = 60  # slightly taller for bigger fonts

        # Make sure None values are safe
        name = name or ""
        book = book or ""
        style = style or ""
        notes = notes or ""
        url = url or ""

        # Labels (shown initially)
        font_size = 18
        self.name_label = Label(text=name, size_hint_x=0.3, font_size=font_size)
        self.book_label = Label(text=book, size_hint_x=0.2, font_size=font_size)
        self.page_label = Label(text=str(page), size_hint_x=0.1, font_size=font_size)
        self.style_label = Label(text=style, size_hint_x=0.2, font_size=font_size)
        self.notes_label = Label(text=notes, size_hint_x=0.2, font_size=font_size)

        # Inputs (hidden initially)
        self.name_input = TextInput(text=name, size_hint_x=0.3, multiline=False, font_size=font_size)
        self.book_input = TextInput(text=book, size_hint_x=0.2, multiline=False, font_size=font_size)
        self.page_input = TextInput(text=str(page), size_hint_x=0.1, multiline=False, font_size=font_size)
        self.style_input = TextInput(text=style, size_hint_x=0.2, multiline=False, font_size=font_size)
        self.notes_input = TextInput(text=notes, size_hint_x=0.2, multiline=False, font_size=font_size)
        self.url_input = TextInput(text=url, size_hint_x=0.3, multiline=False, font_size=font_size)

        # Buttons
        self.edit_btn = Button(text="Edit", size_hint_x=0.1)
        self.edit_btn.bind(on_release=self.start_edit)

        self.save_btn = Button(text="Save", size_hint_x=0.1)
        self.save_btn.bind(on_release=self.save_edit)

        self.cancel_btn = Button(text="Cancel", size_hint_x=0.1)
        self.cancel_btn.bind(on_release=self.cancel_edit)

        # Add initial labels + edit button
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
        self.add_widget(self.url_input)
        self.add_widget(self.save_btn)
        self.add_widget(self.cancel_btn)

    def save_edit(self, instance):
        # Update DB
        new_name = self.name_input.text.strip()
        new_book = self.book_input.text.strip()
        try:
            new_page = int(self.page_input.text.strip())
        except ValueError:
            new_page = 0
        new_style = self.style_input.text.strip()
        new_notes = self.notes_input.text.strip()
        new_url = self.url_input.text.strip()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            UPDATE Tunes
            SET name=?, page=?, notes=?, url=?
            WHERE id=?
        """, (new_name, new_page, new_notes, new_url, self.tune_id))
        conn.commit()
        conn.close()

        # Update labels
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
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search bar
        self.search_input = TextInput(size_hint_y=None, height=40, multiline=False, font_size=22, hint_text="Search Tunes")
        self.search_input.bind(text=self.update_results)
        root.add_widget(self.search_input)

        # Scrollable results
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        root.add_widget(scroll)

        # Add tune button
        #add_btn = Button(text="Add New Tune", size_hint_y=None, height=50, font_size=20)
        #add_btn.bind(on_release=self.add_tune)  # make sure add_tune() exists
        #root.add_widget(add_btn)

        # Populate rows
        self.update_results()

        return root


    def update_results(self, *args):
        print("Updating results")
        self.grid.clear_widgets()  # very important!

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT Tunes.id, Tunes.name, Books.book_name, Tunes.page,
                Styles.style_name, Tunes.notes, Tunes.url
            FROM Tunes
            LEFT JOIN Books ON Tunes.book_id = Books.id
            LEFT JOIN Styles ON Tunes.style_id = Styles.id
        """)
        rows = c.fetchall()
        conn.close()

        for row in rows:
            # Handle None values safely
            tune_id, name, book, page, style, notes, url = row
            name = name or ""
            book = book or ""
            page = page or 0
            style = style or ""
            notes = notes or ""
            url = url or ""

            tune_row = TuneRow(self, tune_id, name, book, page, style, notes, url)
            self.grid.add_widget(tune_row)



    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    PipeTunesApp().run()
