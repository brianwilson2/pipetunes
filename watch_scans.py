import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyPDF2 import PdfReader, PdfWriter

INPUT_FOLDER = os.path.expanduser("~/pipetunes_in/doubles")
PROCESSED_FOLDER = os.path.expanduser("~/pipetunes_processed")

class ScanHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(".pdf"):
            print(f"New PDF detected: {event.src_path}")
            split_pdf(event.src_path)

def split_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    reader = PdfReader(pdf_path)
    
    for i, page in enumerate(reader.pages):
        # Split vertically (side-by-side tunes)
        width = page.mediabox.width
        height = page.mediabox.height

        # Left tune
        left_page = page
        left_page.mediabox.upper_right = (width/2, height)
        writer_left = PdfWriter()
        writer_left.add_page(left_page)
        left_name = os.path.join(PROCESSED_FOLDER, f"{os.path.splitext(filename)[0]}_1.pdf")
        with open(left_name, "wb") as f:
            writer_left.write(f)

        # Right tune
        right_page = page
        right_page.mediabox.lower_left = (width/2, 0)
        writer_right = PdfWriter()
        writer_right.add_page(right_page)
        right_name = os.path.join(PROCESSED_FOLDER, f"{os.path.splitext(filename)[0]}_2.pdf")
        with open(right_name, "wb") as f:
            writer_right.write(f)
    
    print(f"Finished splitting {filename}")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(ScanHandler(), INPUT_FOLDER, recursive=False)
    observer.start()
    print("Watching folder for new scans... Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
