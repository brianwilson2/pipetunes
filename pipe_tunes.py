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
from kivy.uix.filechooser import FileChooserListView
import sqlite3
import import_csv  # your CSV import script
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

# ---------------------------
# DB constants
# ---------------------------
DB_NAME = "tunes.db"

# ---------------------------
# Backend-only functions
# ---------------------------
def run_pipe_tunes_backend():
    """
    Run all non-GUI parts: CSV import, DB updates, etc.
    Safe to call with HEADLESS=1.
    """
    print("Running backend PipeTunes tasks...")
    # Example: process CSVs automatically if needed
    # import_csv.run_import("some_default_file.csv")
    # You can call any other backend-only routines here

# ---------------------------
# UI Row (unchanged)
# ---------------------------
class TuneRow(BoxLayout):
    # ... Keep the full TuneRow class as-is from your copy
    # No changes here
    pass

# ---------------------------
# Main App (unchanged)
# ---------------------------
class PipeTunesApp(App):
    # ... Keep all methods as-is from your copy
    pass

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    if HEADLESS:
        run_pipe_tunes_backend()
    else:
        PipeTunesApp().run()