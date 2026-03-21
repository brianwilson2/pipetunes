from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import sqlite3
import webbrowser

DB_NAME = "tunes.db"

from functools import partial

# ---------------------------
# UI Row
# ---------------------------
class TuneRow(BoxLayout):
    def __init__(self, app, tune_id, name, page, style, book, notes, url, url_label, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.tune_id = tune_id
        self.is_editing = False
        self.orientation = 'horizontal'
        self.spacing = 10
        self.padding = [10,5,5,5]
        self.size_hint_y = None
        self.height = 70

        # Labels / Buttons for viewing
        self.name_label = Label(text=name, size_hint_x=0.35)
        self.book_label = Label(text=book, size_hint_x=0.25)
        self.page_label = Label(text=str(page), size_hint_x=0.08)
        self.style_label = Label(text=style, size_hint_x=0.12)
        self.notes_label = Label(text=notes, size_hint_x=0.25)
        self.url_btn = Button(text=url_label, size_hint_x=0.25)
        self.url_btn.bind(on_release=lambda instance: webbrowser.open(url))

        # Inputs for editing
        self.name_input = TextInput(text=name, size_hint_x=0.35, multiline=False)
        self.book_input = TextInput(text=book, size_hint_x=0.25, multiline=False)
        self.page_input = TextInput(text=str(page), size_hint_x=0.08, multiline=False)
        self.style_input = TextInput(text=style, size_hint_x=0.12, multiline=False)
        self.notes_input = TextInput(text=notes, size_hint_x=0.25, multiline=False)
        self.url_input = TextInput(text=url, size_hint_x=0.25, multiline=False)

        # Buttons
        self.edit_btn = Button(text="Edit", size_hint_x=0.1)
        self.edit_btn.bind(on_release=self.start_edit)

        self.save_btn = Button(text="Save", size_hint_x=0.1)
        self.save_btn.bind(on_release=self.save_edit)

        self.cancel_btn = Button(text="Cancel", size_hint_x=0.1)
        self.cancel_btn.bind(on_release=self.cancel_edit)

        self.show_view_mode()

    def show_view_mode(self):
        self.clear_widgets()
        self.add_widget(self.name_label)
        self.add_widget(self.book_label)
        self.add_widget(self.page_label)
        self.add_widget(self.style_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.url_btn)
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
            UPDATE Tunes SET name=?, page=?, style_id=?, book_id=?, notes=?, url=? WHERE id=?
        ''', (new_name, new_page, style_id, book_id, new_notes, new_url, self.tune_id))
        conn.commit()
        conn.close()

        # Update labels/buttons
        self.name_label.text = new_name
        self.book_label.text = new_book
        self.page_label.text = str(new_page)
        self.style_label.text = new_style
        self.notes_label.text = new_notes
        self.url_btn.text = new_url if new_url else f"{new_name.replace(' ','')[:15]}.pdf"
        self.end_edit()

    def cancel_edit(self, instance):
        self.end_edit()

    def end_edit(self):
        self.is_editing = False
        self.show_view_mode()


# ---------------------------
# Main App
# ---------------------------
class PipeTunesApp(App):
    def build(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.search_event = None

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search + clear button
        search_box = BoxLayout(size_hint_y=None, height=40, spacing=5)
        self.search_input = TextInput(hint_text="Search tune...", multiline=False)
        self.search_input.bind(text=self.on_search_text)
        clear_btn = Button(text="Clear", size_hint_x=0.15)
        clear_btn.bind(on_release=lambda instance: self.clear_search())
        search_box.add_widget(self.search_input)
        search_box.add_widget(clear_btn)
        root.add_widget(search_box)

        # Scrollable grid
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        # Add Tune button
        add_btn = Button(text="Add New Tune", size_hint_y=None, height=40)
        add_btn.bind(on_release=self.add_tune)
        root.add_widget(add_btn)

        # Initial load
        Clock.schedule_once(lambda dt: self.update_results(), 0)
        return root

    def add_grid_header(self):
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=40, spacing=10, padding=[10,0,5,0]
        )
        header.add_widget(Label(text="Tune Name", size_hint_x=0.35))
        header.add_widget(Label(text="Book Name", size_hint_x=0.25))
        header.add_widget(Label(text="Page No", size_hint_x=0.08))
        header.add_widget(Label(text="Style", size_hint_x=0.12))
        header.add_widget(Label(text="Notes", size_hint_x=0.25))
        header.add_widget(Label(text="URL to Music", size_hint_x=0.25))
        self.grid.add_widget(header)

    # ---------------------------
    # Search with delay
    # ---------------------------
    def on_search_text(self, instance, value):
        if self.search_event:
            self.search_event.cancel()
        self.search_event = Clock.schedule_once(lambda dt: self.update_results(), 0.5)

    def clear_search(self):
        self.search_input.text = ""
        self.update_results()

    # ---------------------------
    # Update results
    # ---------------------------
    def update_results(self):
        self.grid.clear_widgets()
        self.add_grid_header()
        query = self.search_input.text.strip().lower()
        c = self.conn.cursor()
        if query:
            c.execute('''
                SELECT t.id, t.name, t.page, s.style_name, b.book_name, t.notes, t.url
                FROM Tunes t
                JOIN Styles s ON t.style_id = s.id
                JOIN Books b ON t.book_id = b.id
                WHERE LOWER(t.name) LIKE ?
                ORDER BY t.name
                LIMIT 100
            ''', (f"%{query}%",))
        else:
            c.execute('''
                SELECT t.id, t.name, t.page, s.style_name, b.book_name, t.notes, t.url
                FROM Tunes t
                JOIN Styles s ON t.style_id = s.id
                JOIN Books b ON t.book_id = b.id
                ORDER BY t.name
                LIMIT 100
            ''')

        for row in c.fetchall():
            t_id, name, page, style, book, notes, url = [str(r) if r is not None else "" for r in row]
            
            # Only make a short label if there’s a URL
            short_label = url.split('/')[-1] if url else ""
            
            tune_row = TuneRow(
                app=self, tune_id=t_id, name=name, page=page,
                style=style, book=book, notes=notes,
                url=url, url_label=short_label
            )
            self.grid.add_widget(tune_row)
    

    def add_tune(self, instance):
        c = self.conn.cursor()
        c.execute("INSERT INTO Tunes(name,page,book_id,style_id,notes,url) VALUES (?,?,?,?,?,?)",
                  ("New Tune",0,None,None,"",""))
        tune_id = c.lastrowid
        self.conn.commit()
        safe_name = "NewTune"
        short_label = f"{safe_name}.pdf"
        tune_row = TuneRow(self, tune_id, "New Tune", 0, "", "", "", "", f"https://www.eadar-lion.com/pipetunes/{safe_name}.pdf", short_label)
        self.grid.add_widget(tune_row)

    def on_stop(self):
        self.conn.close()


if __name__ == "__main__":
    from kivy.core.window import Window
    Window.size = (1200, 800)
    PipeTunesApp().run()