import os
import re
import json

INPUT_DIR = "./converted_docs"
OUTPUT_DIR = "./cleaned_json"


def clean_and_convert_to_json(file_path, legislative_id, session, version, filename):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    clean_text = re.sub(r"!\[\]\(data:image\/png;base64,[^)]+\)", "", content)

    lines = clean_text.split("\n")

    long_title = lines[2].strip("**") if len(lines) >= 3 else None

    short_title_match = re.search(r"\*\*Short Title\*\*: (.*?)\n", clean_text)
    sponsors_match = re.search(r"\*\*Sponsors\*\*:(.*?)\n", clean_text, re.DOTALL)
    secondary_sponsors_match = re.search(
        r"\*\*Secondary Sponsors\*\*:(.*?)\n", clean_text, re.DOTALL
    )
    first_reading_match = re.search(r"\*\*First Reading\*\*: (.*?)\n", clean_text)
    second_reading_match = re.search(r"\*\*Second Reading\*\*: (.*?)\n", clean_text)
    result_match = re.search(r"\*\*Result:\*\* (.*?)\n", clean_text)

    whereas_clauses = re.findall(
        r"^\*\*\s*WHEREAS,?\*\*\s*(.*?);", clean_text, re.MULTILINE
    )
    enacted_clauses = re.findall(
        r"^\*\*\s*ENACTED,?\*\*\s*(.*?);", clean_text, re.MULTILINE
    )
    resolved_clauses = re.findall(
        r"^\*\*\s*RESOLVED,?\*\*\s*(.*?);", clean_text, re.MULTILINE
    )

    data = {
        "id": f"{legislative_id}_{session}_{version}".lower(),
        "version": version,
        "long_title": long_title,
        "short_title": short_title_match.group(1) if short_title_match else None,
        "sponsors": (
            [s.strip() for s in sponsors_match.group(1).split(",")]
            if sponsors_match
            else []
        ),
        "secondary_sponsors": (
            [s.strip() for s in secondary_sponsors_match.group(1).split(",")]
            if secondary_sponsors_match
            else []
        ),
        "first_reading": first_reading_match.group(1) if first_reading_match else None,
        "second_reading": (
            second_reading_match.group(1) if second_reading_match else None
        ),
        "result": result_match.group(1) if result_match else None,
        "whereas_clauses": whereas_clauses,
        "enacted_clauses": enacted_clauses,
        "resolved_clauses": resolved_clauses,
        "filename": filename,
        "session": session,
    }

    return data


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
                if file.endswith(".md"):
                    file_path = os.path.join(folder_path, file)
                    version = get_version_from_filename(file)
                    data = clean_and_convert_to_json(
                        file_path, legislative_id, session, version, file
                    )

                    if is_overly_empty(data):
                        if not os.path.exists("./unprocessed"):
                            os.makedirs("./unprocessed")
                        output_file = os.path.join(
                            "./unprocessed",
                            f"{legislative_id}_{session}_{version}.json",
                        )
                    else:
                        output_file = os.path.join(
                            OUTPUT_DIR, f"{legislative_id}_{session}_{version}.json"
                        )
                    with open(output_file, "w", encoding="utf-8") as out:
                        json.dump(data, out, indent=4)

                    print(f"Processed {file_path} -> {output_file}")


def is_overly_empty(data):
    essential_fields = [
        "long_title",
        "short_title",
        "sponsors",
        "whereas_clauses",
        "resolved_clauses",
    ]
    for field in essential_fields:
        if isinstance(data[field], list) and not data[field]:
            continue
        if not data[field]:
            return True
    return False


if __name__ == "__main__":
    process_directory()
