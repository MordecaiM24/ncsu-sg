import os
import re
import json

INPUT_DIR = "./downloaded_docs"
OUTPUT_DIR = "../aws/pdfs"


def get_version_from_filename(filename):
    if "FIRST_READING" in filename:
        return "first_reading"
    elif "SECOND_READING" in filename:
        return "second_reading"
    elif "OFFICIATED" in filename:
        return "officiated"
    elif "VETOED" in filename:
        return "vetoed"
    elif "FAILED" in filename:
        return "failed"
    elif "ENGROSSED" in filename:
        return "engrossed"
    else:
        return "unknown"


def process_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for legislative_id in os.listdir(INPUT_DIR):
        session = "104"
        folder_path = os.path.join(INPUT_DIR, legislative_id)

        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith(".pdf"):
                    file_path = os.path.join(folder_path, file)
                    version = get_version_from_filename(file)
                    id = f"{legislative_id}_{session}_{version}".lower()

                    output_file = os.path.join(OUTPUT_DIR, f"{id}.pdf".replace(",", ""))
                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                    with open(file_path, "rb") as src, open(output_file, "wb") as dst:
                        dst.write(src.read())

                    print(f"Processed {file_path} -> {output_file}")


if __name__ == "__main__":
    process_directory()
