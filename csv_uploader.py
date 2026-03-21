from pathlib import Path
from kivy.uix.filechooser import FileChooserListView

class CSVUploader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Try to use last folder used, else default to pipes folder
        self.last_folder_file = Path.home() / ".last_csv_folder.txt"
        if self.last_folder_file.exists():
            last_folder = self.last_folder_file.read_text().strip()
            if not Path(last_folder).exists():
                last_folder = str(Path.home() / "arduino-python/pipes")
        else:
            last_folder = str(Path.home() / "arduino-python/pipes")
        
        self.filechooser = FileChooserListView(path=last_folder, filters=['*.csv'])
        self.add_widget(self.filechooser)

    def upload_csv(self):
        selection = self.filechooser.selection
        if not selection:
            self.add_log("No file selected...")
            return
        
        csv_path = selection[0]
        self.add_log(f"Uploading {csv_path}...")
        
        # Save folder for next time
        folder = str(Path(csv_path).parent)
        self.last_folder_file.write_text(folder)
        
        # ... proceed to parse CSV and insert into DB