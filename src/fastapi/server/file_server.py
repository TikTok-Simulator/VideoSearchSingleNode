from flask import Flask, send_file, jsonify, abort
import os
import socket
from pathlib import Path

app = Flask(__name__)

# Configure the directory to serve files from
# TODO: CHANGE THIS
BASE_DIR = Path(__file__).parent.parent.parent.parent / "video-fetch-and-trim"
PORT = 5678


def is_valid_path(path):
    """Check if the path is valid and within BASE_DIR"""
    full_path = os.path.join(BASE_DIR, path)
    return os.path.exists(full_path) and os.path.abspath(full_path).startswith(
        os.path.abspath(BASE_DIR)
    )


@app.route("/files/<path:file_path>", methods=["GET"])
def get_file(file_path):
    """Serve a specific file"""
    # if not is_valid_path(file_path):
    #     abort(404, description="File not found or access denied")

    file_full_path = os.path.join(BASE_DIR, file_path)
    if os.path.isfile(file_full_path):
        return send_file(file_full_path)
    else:
        abort(404, description="Not a file")


@app.route("/list/<path:dir_path>", methods=["GET"])
def list_files(dir_path):
    """List files in a directory"""
    # print(dir_path)
    # if not is_valid_path(dir_path):
    #     abort(404, description="Directory not found or access denied")

    dir_full_path = os.path.join(BASE_DIR, dir_path)
    print(dir_full_path)
    if not os.path.isdir(dir_full_path):
        abort(404, description="Not a directory")

    files = []
    for item in os.listdir(dir_full_path):
        item_path = os.path.join(dir_full_path, item)
        files.append(
            {
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path),
                "last_modified": os.path.getmtime(item_path),
            }
        )

    return jsonify(files)


@app.route("/")
def index():
    """Show server info"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return jsonify({"server": hostname, "ip": ip_address, "base_path": BASE_DIR})


if __name__ == "__main__":
    # Get local IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # Run server on all interfaces
    app.run(host="0.0.0.0", port=PORT, debug=True)
