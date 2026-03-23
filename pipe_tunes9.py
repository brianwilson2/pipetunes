from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
import sqlite3
import import_csv  # your CSV import script
from kivy.uix.filechooser import FileChooserListView
import os

# ---------------------------
# Headless-safe setup
# ---------------------------
HEADLESS = os.environ.get("HEADLESS", "0") == "1"

if not HEADLESS:
    try:
        Window.size = (1200, 800)
    except Exception:
        print("Warning: Window setup failed, continuing anyway")
else:
    print("Headless mode: skipping Window setup")

#
DB_NAME = "tunes.db"
#Window.size = (1200, 800)

# ---------------------------
# UI Row
# ---------------------------
class TuneRow(BoxLayout):
    def __init__(self, app, tune_id, name, page, style, book, notes, url, fav=False, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.tune_id = tune_id
        self.is_editing = False
        self.orientation = 'horizontal'
        self.spacing = 5
        self.padding = [5,5,5,5]
        self.size_hint_y = None
        self.height = 50

        # Labels
        self.name_label = Label(text=name or "", size_hint_x=0.25)
        self.book_label = Label(text=book or "", size_hint_x=0.3)
        self.page_label = Label(text=str(page) or "", size_hint_x=0.1)
        self.style_label = Label(text=style or "", size_hint_x=0.15)
        self.notes_label = Label(text=notes or "", size_hint_x=0.1)
        self.url_btn = Button(text="✅", size_hint_x=0.05) if url else Label(text="", size_hint_x=0.05)
        if url:
            self.url_btn.bind(on_release=lambda x: self.open_url(url))
        self.fav_checkbox = CheckBox(active=bool(fav), size_hint_x=0.05)

        self.edit_btn = Button(text="Edit", size_hint_x=0.1)
        self.edit_btn.bind(on_release=self.start_edit)
        self.save_btn = Button(text="Save", size_hint_x=0.1)
        self.save_btn.bind(on_release=self.save_edit)
        self.cancel_btn = Button(text="Cancel", size_hint_x=0.1)
        self.cancel_btn.bind(on_release=self.cancel_edit)

        # Inputs
        self.name_input = TextInput(text=name or "", size_hint_x=0.25, multiline=False)
        self.book_input = TextInput(text=book or "", size_hint_x=0.3, multiline=False)
        self.page_input = TextInput(text=str(page) or "", size_hint_x=0.1, multiline=False)
        self.style_input = TextInput(text=style or "", size_hint_x=0.15, multiline=False)
        self.notes_input = TextInput(text=notes or "", size_hint_x=0.1, multiline=False)
        self.url_input = TextInput(text=url or "", size_hint_x=0.05, multiline=False)
        self.fav_input = CheckBox(active=bool(fav), size_hint_x=0.05)

        # Add widgets (view mode)
        self.add_widget(self.name_label)
        self.add_widget(self.book_label)
        self.add_widget(self.page_label)
        self.add_widget(self.style_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.url_btn)
        self.add_widget(self.fav_checkbox)
        self.add_widget(self.edit_btn)

    def open_url(self, url):
        import webbrowser
        webbrowser.open(f"https://www.eadar-lion.com/pipetunes/{url}")

    def start_edit(self, instance):
        if self.is_editing:
            return
        self.is_editing = True
        self.clear_widgets()

        # Add inputs
        self.add_widget(self.name_input)
        self.add_widget(self.book_input)
        self.add_widget(self.page_input)
        self.add_widget(self.style_input)
        self.add_widget(self.notes_input)
        self.add_widget(self.url_input)
        self.add_widget(self.fav_input)

        # Add buttons
        self.add_widget(self.save_btn)
        self.add_widget(self.cancel_btn)

        # --- New Delete Button ---
        self.delete_btn = Button(text="Delete", size_hint_x=0.1)
        self.delete_btn.bind(on_release=self.delete_tune)
        self.add_widget(self.delete_btn)

    # Delete function
    def delete_tune(self, instance):
        conn = sqlite3.connect("tunes.db")
        c = conn.cursor()
        c.execute("DELETE FROM Tunes WHERE id=?", (self.tune_id,))
        conn.commit()
        conn.close()

        # Remove row from UI
        self.parent.remove_widget(self)

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
        new_fav = self.fav_input.active

        # Update DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO Styles(style_name) VALUES(?)", (new_style,))
        c.execute("SELECT id FROM Styles WHERE style_name=?", (new_style,))
        style_id = c.fetchone()[0]

        c.execute("INSERT OR IGNORE INTO Books(book_name) VALUES(?)", (new_book,))
        c.execute("SELECT id FROM Books WHERE book_name=?", (new_book,))
        book_id = c.fetchone()[0]

        c.execute('''
            UPDATE Tunes SET name=?, page=?, style_id=?, book_id=?, notes=?, url=?, favorite=?
            WHERE id=?
        ''', (new_name, new_page, style_id, book_id, new_notes, new_url, int(new_fav), self.tune_id))
        conn.commit()
        conn.close()

        # Update labels
        self.name_label.text = new_name
        self.book_label.text = new_book
        self.page_label.text = str(new_page)
        self.style_label.text = new_style
        self.notes_label.text = new_notes
        if new_url:
            self.url_btn = Button(text="✅", size_hint_x=0.05)
            self.url_btn.bind(on_release=lambda x: self.open_url(new_url))
        else:
            self.url_btn = Label(text="", size_hint_x=0.05)
        self.fav_checkbox.active = new_fav
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
        self.add_widget(self.url_btn)
        self.add_widget(self.fav_checkbox)
        self.add_widget(self.edit_btn)
        self.is_editing = False


# ---------------------------
# Main App
# ---------------------------
class PipeTunesApp(App):
    def build(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.last_search_event = None

        root = BoxLayout(orientation='vertical', padding=10, spacing=5)

        # Header
        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text="Tune Name", size_hint_x=0.25))
        header.add_widget(Label(text="Book Name", size_hint_x=0.3))
        header.add_widget(Label(text="Page", size_hint_x=0.1))
        header.add_widget(Label(text="Style", size_hint_x=0.15))
        header.add_widget(Label(text="Notes", size_hint_x=0.1))
        header.add_widget(Label(text="URL", size_hint_x=0.05))
        header.add_widget(Label(text="Fav", size_hint_x=0.05))
        header.add_widget(Label(text="#Edit", size_hint_x=0.1))
        root.add_widget(header)

        # Search row
        search_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
        self.search_input = TextInput(hint_text="Search tune...", multiline=False)
        self.search_input.bind(text=self.schedule_search)
        clear_btn = Button(text="Clear", size_hint_x=0.1)
        clear_btn.bind(on_release=lambda x: self.clear_search())
        search_row.add_widget(self.search_input)
        search_row.add_widget(clear_btn)
        root.add_widget(search_row)

        # ... inside PipeTunesApp.build() somewhere above the RecycleView/ScrollView setup
        csv_btn = Button(text="Import CSV", size_hint_y=None, height=40)
        csv_btn.bind(on_release=lambda x: self.import_csv_file())
        root.add_widget(csv_btn)


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

        # Import CSV button - add after Add New Tune button
        import_btn = Button(text="Import CSV", size_hint_y=None, height=40)
        import_btn.bind(on_release=self.import_csv_file)
        root.add_widget(import_btn)

        # Initial results
        self.update_results()
        return root

    def schedule_search(self, *args):
        if self.last_search_event:
            self.last_search_event.cancel()
        self.last_search_event = Clock.schedule_once(lambda dt: self.update_results(), 0.5)

    def clear_search(self):
        self.search_input.text = ""
        self.update_results()

    def update_results(self, *args):
        self.grid.clear_widgets()
        query = self.search_input.text.strip().lower()
        c = self.conn.cursor()

        sql = '''
            SELECT t.id, t.name, t.page, s.style_name, b.book_name, t.notes, t.url, t.favorite
            FROM Tunes t
            LEFT JOIN Styles s ON t.style_id = s.id
            LEFT JOIN Books b ON t.book_id = b.id
        '''
        params = ()
        if query:
            sql += " WHERE LOWER(t.name) LIKE ? OR LOWER(b.book_name) LIKE ? OR LOWER(s.style_name) LIKE ?"
            params = (f"%{query}%", f"%{query}%", f"%{query}%")
        sql += " ORDER BY t.name LIMIT 200"
        c.execute(sql, params)

        for row in c.fetchall():
            t_id, name, page, style, book, notes, url, fav = [item or "" for item in row]
            tune_row = TuneRow(self, t_id, name, page, style, book, notes, url, fav)
            self.grid.add_widget(tune_row)

    def add_tune(self, instance):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO Tunes(name, page, style_id, book_id, notes, url, favorite) VALUES(?,?,?,?,?,?,?)",
                  ("New Tune", 0, None, None, "", "", 0))
        tune_id = c.lastrowid
        conn.commit()
        conn.close()
        self.grid.add_widget(TuneRow(self, tune_id, "New Tune", 0, "", "", "", "", 0))

    def import_csv_file(self):
        chooser = FileChooserListView(path='.', filters=['*.csv'])
        popup = Popup(title="Select CSV file", content=chooser, size_hint=(0.9,0.9))
        
        def load_selection(instance, selection):
            if selection:
                popup.dismiss()
                import_csv(selection[0])
                self.update_results()  # refresh the tune list

        chooser.bind(on_submit=load_selection)
        popup.open()

    def on_stop(self):
        self.conn.close()

    # Add this method to PipeTunesApp
    # inside PipeTunesApp class
    def import_csv_file(self, *args):
        from import_csv import run_import
        
        chooser = FileChooserListView(path='.', filters=['*.csv'])
        popup = Popup(title="Select CSV file", content=chooser, size_hint=(0.9,0.9))

        def load_selection(instance, selection, touch=None):
            if selection:
                popup.dismiss()
                skipped = run_import(selection[0])
                self.update_results()  # refresh tunes

                if skipped:
                    scroll = ScrollView(size_hint=(1,1))
                    grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
                    grid.bind(minimum_height=grid.setter('height'))
                    for tname, book in skipped:
                        grid.add_widget(Label(text=f"{tname} ({book})", size_hint_y=None, height=30))
                    close_btn = Button(text="Close", size_hint_y=None, height=40)
                    grid.add_widget(close_btn)
                    skipped_popup = Popup(title=f"{len(skipped)} Duplicate Tunes Skipped",
                                        content=grid, size_hint=(0.7,0.7))
                    close_btn.bind(on_release=skipped_popup.dismiss)
                    skipped_popup.open()

        chooser.bind(on_submit=load_selection)
        popup.open()



if __name__ == "__main__":
    PipeTunesApp().run()