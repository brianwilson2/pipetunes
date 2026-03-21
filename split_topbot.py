from PyPDF2 import PdfReader, PdfWriter
import os

INPUT_FOLDER = os.path.expanduser("~/arduino-python/pipes/pipetunes_IN/doubles")
OUTPUT_FOLDER = os.path.expanduser("~/arduino-python/pipes/pipetunes_processed")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith(".pdf"):
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    reader = PdfReader(input_path)

    for i, page in enumerate(reader.pages):
        width = page.mediabox.width
        height = page.mediabox.height

        # Top half
        top_page = page
        top_page.mediabox.lower_left = (0, height/2)
        top_page.mediabox.upper_right = (width, height)
        writer_top = PdfWriter()
        writer_top.add_page(top_page)
        top_name = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}_1.pdf")
        with open(top_name, "wb") as f:
            writer_top.write(f)

        # Bottom half
        bottom_page = page
        bottom_page.mediabox.lower_left = (0, 0)
        bottom_page.mediabox.upper_right = (width, height/2)
        writer_bottom = PdfWriter()
        writer_bottom.add_page(bottom_page)
        bottom_name = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}_2.pdf")
        with open(bottom_name, "wb") as f:
            writer_bottom.write(f)

    print(f"Split {filename} top/bottom")