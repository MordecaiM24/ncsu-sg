import os
import logging
import json
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm


CREDS_FILE = "./credentials.json"
DOWNLOAD_DIR = "./downloaded_docs"
MAPPING_FILE = "./drive_mapping.json"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)


GOOGLE_MIME_TYPES = {
    "application/vnd.google-apps.document": {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
    },
    "application/vnd.google-apps.spreadsheet": {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
    },
    "application/vnd.google-apps.presentation": {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
    },
}


def list_files_in_folder_via_search(folder_id):
    logging.info(f"Searching for files in folder ID: {folder_id}")
    files = []
    query = f"'{folder_id}' in parents and trashed = false"

    try:
        page_token = None
        while True:
            response = (
                drive_service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                    pageSize=1000,
                    pageToken=page_token,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )

            found_files = response.get("files", [])
            logging.info(f"  Found {len(found_files)} files in this batch")
            files.extend(found_files)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        logging.info(f"Total files found in folder: {len(files)}")

    except Exception as e:
        logging.error(f"Error searching for files in folder {folder_id}: {e}")

    return files


def map_drive_folder(folder_id, folder_path="", mapping=None):
    """
    Recursively map the folder structure of Google Drive
    Returns a dictionary with the full structure
    """
    if mapping is None:
        mapping = {}

    current_folder = {"files": [], "folders": {}}
    mapping[folder_path] = current_folder

    files = list_files_in_folder_via_search(folder_id)

    for file in files:
        if file["mimeType"] == "application/vnd.google-apps.folder":
            subfolder_name = file["name"]
            subfolder_path = os.path.join(folder_path, subfolder_name)

            map_drive_folder(file["id"], subfolder_path, mapping)

            current_folder["folders"][subfolder_name] = {
                "id": file["id"],
                "path": subfolder_path,
            }
        else:

            file_info = {
                "id": file["id"],
                "name": file["name"],
                "mimeType": file["mimeType"],
                "modifiedTime": file["modifiedTime"],
            }
            current_folder["files"].append(file_info)

    return mapping


def save_mapping(mapping, file_path):
    """Save the drive mapping to a JSON file"""
    with open(file_path, "w") as f:
        json.dump(mapping, f, indent=2)
    logging.info(f"Drive mapping saved to {file_path}")


def load_mapping(file_path):
    """Load drive mapping from a JSON file if it exists"""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def get_local_files(base_dir):
    """
    Create a mapping of all local files in the directory structure
    Returns a dictionary of {relative_path: [filenames]}
    """
    local_files = {}

    for root, _, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == ".":
            rel_path = ""

        local_files[rel_path] = files

    return local_files


def download_regular_file(file_id, file_name, dest_dir):
    file_path = os.path.join(dest_dir, file_name)
    os.makedirs(dest_dir, exist_ok=True)

    logging.info(f"Downloading regular file: {file_name}")

    try:
        request = drive_service.files().get_media(fileId=file_id)
        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"    Download progress: {int(status.progress() * 100)}%")

        logging.info(f"Downloaded: {file_name} -> {file_path}")
        return True

    except Exception as e:
        logging.error(f"Error downloading file {file_name}: {e}")
        return False


def export_google_doc(file_id, file_name, mime_type, dest_dir, export_format):

    base_name = os.path.splitext(file_name)[0]
    export_file_name = f"{base_name}.{export_format}"
    file_path = os.path.join(dest_dir, export_file_name)

    logging.info(f"Exporting Google {export_format} file: {export_file_name}")

    try:
        export_mime = GOOGLE_MIME_TYPES[mime_type][export_format]
        request = drive_service.files().export_media(
            fileId=file_id, mimeType=export_mime
        )

        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(
                    f"    Export progress ({export_format}): {int(status.progress() * 100)}%"
                )

        logging.info(f"Exported: {export_file_name} -> {file_path}")
        return True

    except Exception as e:
        logging.error(f"Error exporting {export_format} for {file_name}: {e}")
        return False


def download_file(file_id, file_name, mime_type, dest_dir, local_files):
    os.makedirs(dest_dir, exist_ok=True)

    if mime_type in GOOGLE_MIME_TYPES:
        logging.info(f"Processing Google Docs file: {file_name} (ID: {file_id})")

        base_name = os.path.splitext(file_name)[0]
        export_formats = list(GOOGLE_MIME_TYPES[mime_type].keys())
        all_formats_exist = True

        dir_files = local_files.get(os.path.relpath(dest_dir, DOWNLOAD_DIR), [])

        for export_format in export_formats:
            export_file_name = f"{base_name}.{export_format}"
            if export_file_name not in dir_files:
                all_formats_exist = False
                break

        if all_formats_exist:
            logging.info(f"Skipping already downloaded file: {file_name}")
            return True

        for export_format in export_formats:
            export_google_doc(file_id, file_name, mime_type, dest_dir, export_format)

        return True
    else:
        dir_files = local_files.get(os.path.relpath(dest_dir, DOWNLOAD_DIR), [])
        if file_name in dir_files:
            logging.info(f"Skipping already downloaded file: {file_name}")
            return True

        return download_regular_file(file_id, file_name, dest_dir)


def process_mapping(drive_mapping, local_files, base_dir=DOWNLOAD_DIR):
    """Process the drive mapping and download missing files"""
    files_to_download = []
    folders_to_process = []

    for folder_path, folder_data in drive_mapping.items():
        dest_dir = os.path.join(base_dir, folder_path)

        for file_info in folder_data["files"]:
            file_id = file_info["id"]
            file_name = file_info["name"]
            mime_type = file_info["mimeType"]

            if mime_type in GOOGLE_MIME_TYPES:
                base_name = os.path.splitext(file_name)[0]
                export_formats = list(GOOGLE_MIME_TYPES[mime_type].keys())

                dir_files = local_files.get(folder_path, [])

                all_formats_exist = True
                for export_format in export_formats:
                    export_file_name = f"{base_name}.{export_format}"
                    if export_file_name not in dir_files:
                        all_formats_exist = False
                        break

                if not all_formats_exist:
                    files_to_download.append(
                        {
                            "id": file_id,
                            "name": file_name,
                            "mimeType": mime_type,
                            "dest_dir": dest_dir,
                        }
                    )
            else:

                dir_files = local_files.get(folder_path, [])
                if file_name not in dir_files:
                    files_to_download.append(
                        {
                            "id": file_id,
                            "name": file_name,
                            "mimeType": mime_type,
                            "dest_dir": dest_dir,
                        }
                    )

    logging.info(f"Found {len(files_to_download)} files to download")

    for file_info in tqdm(files_to_download, desc="Downloading files"):
        download_file(
            file_info["id"],
            file_info["name"],
            file_info["mimeType"],
            file_info["dest_dir"],
            local_files,
        )


if __name__ == "__main__":
    FOLDER_ID = "1jUcFATBhQIPgZUbSfWuaEq6ymWyjX3Ar"
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

    logging.info(f"Mapping Google Drive folder structure...")
    drive_mapping = map_drive_folder(FOLDER_ID)

    save_mapping(drive_mapping, MAPPING_FILE)

    logging.info(f"Scanning local directory structure...")
    local_files = get_local_files(DOWNLOAD_DIR)

    logging.info(f"Starting download of missing files...")
    process_mapping(drive_mapping, local_files)

    logging.info("Download complete.")
