import requests

url = (
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
)
local_filename = "TearsOfSteel.mp4"

with requests.get(url, stream=True) as r:
    r.raise_for_status()
    with open(local_filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("Downloaded:", local_filename)
