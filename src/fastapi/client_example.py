import requests

# TODO: Replace with destination server's IP
SERVER_IP = "10.130.92.78"
PORT = 5678
SERVER_URL = f"http://{SERVER_IP}:{PORT}"


def list_files(path=""):
    response = requests.get(f"{SERVER_URL}/list/{path}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.json()['description']}")
        return None


def download_file(file_path, local_path):
    response = requests.get(f"{SERVER_URL}/files/{file_path}", stream=True)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"File downloaded to {local_path}")
    else:
        print(f"Error: {response.status_code} - {response.json()['description']}")


# Example usage
if __name__ == "__main__":
    # List files in root directory
    files = list_files("videos")
    if files:
        print("Files in directory:")
        for file in files:
            print(f"- {file['name']} ({file['type']})")

    # Download a specific file
    download_file("videos/lifestyle_0.mp4", "local_lifestyle_0.mp4")
