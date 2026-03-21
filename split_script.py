import os
import shutil

INPUT_FOLDER = os.path.expanduser("~/arduino-python/pipes/pipetunes_IN/doubles")
OUTPUT_FOLDER = os.path.expanduser("~/arduino-python/pipes/pipetunes_processed")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Map each PDF to the tunes it represents
# Example format: {'filename.pdf': ['Black_Bird', 'Glendaruel_Highlander']}
pdf_map = {
    "flowers_forest-Land_o_Leal.pdf": ["Flowers_of_the_forest", "Land_o_the_Leal"],
    "hornpipe_Blackbird-reel_High_road_to_Linton.pdf": ["Black_Bird", "Glendaruel_Highlander"],
    "march_Murdos_wedding-old_rustic_bridge.pdf": ["Murdos_wedding", "The_Old_Rustic_bridge"],
    "scotland_brave-Black_bear.pdf": ["Scotland_brave", "Black_bear"],
    # add more PDFs here
}

for pdf_file, tunes in pdf_map.items():
    input_path = os.path.join(INPUT_FOLDER, pdf_file)
    if not os.path.exists(input_path):
        print(f"File not found: {pdf_file}")
        continue

    for tune_name in tunes:
        output_path = os.path.join(OUTPUT_FOLDER, f"{tune_name}.pdf")
        shutil.copy(input_path, output_path)
        print(f"Copied {pdf_file} → {tune_name}.pdf")