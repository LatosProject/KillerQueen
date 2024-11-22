import threading
import time
import logging
from .downloader import download_file
from .utils import get_remote_version, replace_and_restart
from killerqueen.config import CHECK_INTERVAL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Updater:

    def __init__(self, local_version, temp_path, check_interval=CHECK_INTERVAL):
        self.local_version = local_version
        self.temp_path = temp_path
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

        logging.debug(f"Updater instance initialized: local_version={self.local_version}, temp_path={self.temp_path}, check_interval={self.check_interval}")

    def start_periodic_check(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                logging.warning("Update check thread is already running and cannot be started again.")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._periodic_check, daemon=True)
            self._thread.start()
            logging.info("Periodic update check thread started.")

    def stop_periodic_check(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._stop_event.set()
                self._thread.join()
                logging.info("Periodic update check thread stopped.")
            else:
                logging.warning("Update check thread is not running and cannot be stopped.")

    def _periodic_check(self):
        logging.debug("Entered periodic update check loop.")
        while not self._stop_event.is_set():
            try:
                self.check_for_update()
            except Exception as e:
                logging.error(f"Error occurred during update check: {e}")
            time.sleep(self.check_interval)

    def check_for_update(self):
        logging.debug("Starting update check...")
        try:
            remote_version = get_remote_version()

            if remote_version is None:
                logging.warning("Unable to fetch remote version, skipping update check.")
                return

            with self._lock:
                logging.info(f"Local version: {self.local_version}, Remote version: {remote_version}")
                if remote_version > self.local_version:
                    logging.info("New version found, starting update download...")
                    self._download_and_replace(remote_version)
                else:
                    logging.info("Already up-to-date.")
        except Exception as e:
            logging.error(f"Exception occurred during update check: {e}")

    def _download_and_replace(self, new_version):
        logging.debug(f"Starting download for new version: {new_version}...")
        try:
            download_file(self.temp_path)
            logging.info("New version downloaded, preparing to replace old version...")
            replace_and_restart()
            logging.info("Old version replaced and restart completed.")
        except Exception as e:
            logging.error(f"Error occurred during download or replacement: {e}")
