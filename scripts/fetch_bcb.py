import requests
import json
from pathlib import Path

def _json_downloader(url, output_path):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f)