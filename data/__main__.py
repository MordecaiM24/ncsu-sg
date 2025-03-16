import os
import logging
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm


CREDS_FILE = "./credentials.json"
DOWNLOAD_DIR = "./downloaded_docs"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)


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
                    fields="nextPageToken, files(id, name, mimeType)",
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


def download_file(file_id, file_name, dest_dir):
    file_path = os.path.join(dest_dir, file_name)
    os.makedirs(dest_dir, exist_ok=True)

    logging.info(f"Downloading file: {file_name}")

    try:
        request = drive_service.files().get_media(fileId=file_id)
        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"    Download progress: {int(status.progress() * 100)}%")

        logging.info(f"Downloaded: {file_name} -> {file_path}")

    except Exception as e:
        logging.error(f"Error downloading file {file_name}: {e}")


def download_folder_via_search(folder_id, dest_dir):
    files = list_files_in_folder_via_search(folder_id)
    if not files:
        logging.warning(f"No files found in folder {folder_id}")
        return

    for file in tqdm(files, desc="Downloading files"):
        if file["mimeType"] == "application/vnd.google-apps.folder":
            subfolder_path = os.path.join(dest_dir, file["name"])
            os.makedirs(subfolder_path, exist_ok=True)
            logging.info(f"Entering subfolder: {file['name']} (ID: {file['id']})")
            download_folder_via_search(file["id"], subfolder_path)
        else:
            download_file(file["id"], file["name"], dest_dir)


if __name__ == "__main__":
    FOLDER_ID = "1jUcFATBhQIPgZUbSfWuaEq6ymWyjX3Ar"
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting download from folder ID: {FOLDER_ID}")
    download_folder_via_search(FOLDER_ID, DOWNLOAD_DIR)
    logging.info("Download complete.")
