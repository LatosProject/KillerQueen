# Copyright (c) 2024 Latos
#
# This file is part of Killerqueen.
#
# Source Code: https://github.com/LatosProject/
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
TASK_NAME = "SystemUpdateCheck"
EXE_PATH = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\killerqueen\killerqueen.exe")
TEMP_EXE_PATH = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\killerqueen\temp.exe")
SERVER_URL =None #BASE64
LOCAL_VERSION = 5.0
UPLOAD_URL = None #BASE64
USERNAME = None #BASE64
PASSWORD = None #BASE64
CACHE_DIR = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\killerqueen\.cache")
PING_TIMEOUT =5
CHECK_INTERVAL=3600
OFFICE_EXTENSIONS = {}
# e.g OFFICE_EXTENSIONS = {"zip"}
