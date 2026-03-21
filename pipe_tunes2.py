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
import csv

DB_NAME = "tunes.db"
CSV_FILE = "tunes_clean.csv"


# ---------------------------
# Database functions
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Styles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Styles (
            id INTEGER PRIMARY KEY,
            style_name TEXT UNIQUE
        )
    ''')

    # Books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            id INTEGER PRIMARY KEY,
            book_name TEXT UNIQUE
        )
    ''')

    # Tunes table — note style_id and book_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS Tunes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            page INTEGER,
            style_id INTEGER,
            book_id INTEGER,
            notes TEXT,
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
            if row is None:
                continue  # skip empty row
            name = (row.get("tune_name") or "").strip()
            page_str = (row.get("page") or "0").strip()
            notes = (row.get("notes") or "").strip()
            if not name:
                continue
            try:
                page = int(page_str)
            except:
                page = 0
            tunes.append({
                "tune_name": name,
                "page": page,
                "notes": notes
            })
    return tunes


def insert_tunes_into_db(tunes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for t in tunes:
        # style
        c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (t.get("style",""),))
        c.execute("SELECT id FROM Styles WHERE style_name=?", (t.get("style",""),))
        style_id = c.fetchone()[0]

        # book
        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (t.get("booknames",""),))
        c.execute("SELECT id FROM Books WHERE book_name=?", (t.get("booknames",""),))
        book_id = c.fetchone()[0]

        # tune
        c.execute('''
            INSERT INTO Tunes(name, page, style_id, book_id, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (t.get("tune_name",""), t.get("page",0), style_id, book_id, t.get("notes","")))

    conn.commit()
    conn.close()



# ---------------------------
# UI Row
# ---------------------------
class TuneRow(BoxLayout):
    def __init__(self, app, tune_id, name, page=0, book="", notes="", **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.tune_id = tune_id
        self.is_editing = False
        self.orientation = 'horizontal'
        self.spacing = 10
        self.padding = [5, 5, 5, 5]
        self.size_hint_y = None
        self.height = 50

        # Labels (store once)
        self.name_label = Label(text=name, size_hint_x=0.3)
        self.page_label = Label(text=str(page), size_hint_x=0.1)
        self.book_label = Label(text=book, size_hint_x=0.3)
        self.notes_label = Label(text=notes, size_hint_x=0.3)

        # Inputs (hidden initially)
        self.name_input = TextInput(text=name, size_hint_x=0.3, multiline=False)
        self.page_input = TextInput(text=str(page), size_hint_x=0.1, multiline=False)
        self.book_input = TextInput(text=book, size_hint_x=0.3, multiline=False)
        self.notes_input = TextInput(text=notes, size_hint_x=0.3, multiline=False)

        # Buttons
        self.edit_btn = Button(text="Edit", size_hint_x=0.15)
        self.edit_btn.bind(on_release=self.start_edit)
        self.save_btn = Button(text="Save", size_hint_x=0.15)
        self.save_btn.bind(on_release=self.save_edit)
        self.cancel_btn = Button(text="Cancel", size_hint_x=0.15)
        self.cancel_btn.bind(on_release=self.cancel_edit)

        # Initial view
        self.show_labels()

    def show_labels(self):
        """Add existing labels and edit button to layout."""
        self.clear_widgets()
        self.add_widget(self.name_label)
        self.add_widget(self.page_label)
        self.add_widget(self.book_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.edit_btn)

    def start_edit(self, instance):
        if self.is_editing:
            return
        self.is_editing = True
        self.clear_widgets()
        self.add_widget(self.name_input)
        self.add_widget(self.page_input)
        self.add_widget(self.book_input)
        self.add_widget(self.notes_input)
        self.add_widget(self.save_btn)
        self.add_widget(self.cancel_btn)

    def save_edit(self, instance):
        # Read inputs
        new_name = self.name_input.text.strip()
        try:
            new_page = int(self.page_input.text.strip())
        except ValueError:
            new_page = 0
        new_book = self.book_input.text.strip()
        new_notes = self.notes_input.text.strip()

        # Update DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (new_book,))
        c.execute("SELECT id FROM Books WHERE book_name=?", (new_book,))
        book_id = c.fetchone()[0]
        c.execute("UPDATE Tunes SET name=?, page=?, book_id=?, notes=? WHERE id=?",
                  (new_name, new_page, book_id, new_notes, self.tune_id))
        conn.commit()
        conn.close()

        # Update labels
        self.name_label.text = new_name
        self.page_label.text = str(new_page)
        self.book_label.text = new_book
        self.notes_label.text = new_notes
        self.end_edit()

    def cancel_edit(self, instance):
        self.end_edit()

    def end_edit(self):
        self.is_editing = False
        self.show_labels()  # <-- reuse the same labels, do not create new ones


# ---------------------------
# Main App
# ---------------------------
class PipeTunesApp(App):
    def update_results(self, *args):
        self.grid.clear_widgets()
        query = self.search_input.text.strip().lower()
        if len(query) < 2:
            return

        c = self.conn.cursor()
        sql = '''
            SELECT t.id, t.name, t.page, b.book_name, s.style_name, t.notes
            FROM Tunes t
            LEFT JOIN Books b ON t.book_id = b.id
            LEFT JOIN Styles s ON t.style_id = s.id
            WHERE LOWER(t.name) LIKE ?
            ORDER BY t.name
            LIMIT 50
        '''
        c.execute(sql, (f"%{query}%",))
        results = c.fetchall()

        for row in results:
            t_id, name, page_number, book, style, notes = row

            tune_row = TuneRow(
                app=self,
                tune_id=t_id,
                name=name,
                page=page_number if page_number else 0,
                book=book if book else "",
                notes=notes if notes else ""
            )
            self.grid.add_widget(tune_row)

    def build(self):
        # recreate DB
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        init_db()
        tunes = load_csv(CSV_FILE)
        insert_tunes_into_db(tunes)

        self.conn = sqlite3.connect(DB_NAME)
        print(f"Loaded {len(tunes)} tunes into database.")

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Search tune name...", size_hint_y=None, height=40)
        self.search_input.bind(text=self.update_results)  # this now works
        root.add_widget(self.search_input)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        self.update_results()
        return root

    
def update_results(self, *args):
    self.grid.clear_widgets()
    query = self.search_input.text.strip().lower()

    # skip short queries
    if len(query) < 2:
        return

    c = self.conn.cursor()
    sql = '''
        SELECT t.id, t.name, t.page, b.book_name, s.style_name, t.notes
        FROM Tunes t
        LEFT JOIN Books b ON t.book_id = b.id
        LEFT JOIN Styles s ON t.style_id = s.id
        WHERE LOWER(t.name) LIKE ?
        ORDER BY t.name
        LIMIT 50
    '''
    c.execute(sql, (f"%{query}%",))
    results = c.fetchall()

    for row in results:
        t_id, name, page_number, book, style, notes = row

        tune_row = TuneRow(
            app=self,
            tune_id=t_id,
            name=name,
            page=page_number if page_number else 0,
            book=book if book else "",
            notes=notes if notes else ""
        )
        self.grid.add_widget(tune_row)



       # ---------------------------
    # Add/Edit/Delete functions
    # ---------------------------
    def add_tune(self, instance):
        # simple example: add blank tune
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO Tunes(name, page, notes) VALUES (?, ?, ?)", ("New Tune", 0, ""))
        tune_id = c.lastrowid
        conn.commit()
        conn.close()
        self.update_results()

    def edit_tune(self, tune_row):
        # prompt simple edit via terminal for demo purposes
        print(f"Editing {tune_row.tune_name}")
        new_name = input(f"New name ({tune_row.tune_name}): ").strip() or tune_row.tune_name
        try:
            new_page = int(input(f"New page ({tune_row.page}): ").strip())
        except:
            new_page = int(tune_row.page)
        new_notes = input(f"New notes ({tune_row.notes}): ").strip() or tune_row.notes

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE Tunes SET name=?, page=?, notes=? WHERE id=?", (new_name, new_page, new_notes, tune_row.tune_id))
        conn.commit()
        conn.close()
        self.update_results()

    def delete_tune(self, tune_row):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM Tunes WHERE id=?", (tune_row.tune_id,))
        conn.commit()
        conn.close()
        self.update_results()

    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    PipeTunesApp().run()
