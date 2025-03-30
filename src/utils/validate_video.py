import logging
import requests
from urllib.parse import urlparse
import cv2
import os

valid_video_types = {"video/mp4", "video/webm", "video/ogg", "video/avi", "video/mpeg"}


def is_valid_video_url(url: str) -> bool:
    """
    Validate if a URL points to a valid video.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a valid video, False otherwise.
    """
    try:
        # Step 1: Check if the URL is well-formed
        parsed_url = urlparse(url)
        if not all(
            [parsed_url.scheme, parsed_url.netloc]
        ):  # Must have scheme and domain
            logging.info(f"Invalid URL format: {url}")
            return False

        # Step 2: Send a HEAD request to check content type
        headers = {"User-Agent": "Mozilla/5.0"}  # Avoid server blocks
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)

        # Fall back to GET with stream if HEAD fails
        if response.status_code != 200:
            response = requests.get(
                url, headers=headers, stream=True, timeout=5, allow_redirects=True
            )

        # Check status code
        if response.status_code != 200:
            logging.info(f"URL returned status code {response.status_code}: {url}")
            return False

        # Step 3: Check content type
        content_type = response.headers.get("Content-Type", "").lower()
        if content_type not in valid_video_types:
            logging.info(f"URL is not a video, content-type: {content_type}")
            return False

        return True
    except requests.exceptions.RequestException as e:
        logging.info(f"Network error: {e}")
        return False
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        return False
    finally:
        pass


def is_valid_video_file(file_path: str) -> bool:
    """
    Validate if a local file is a valid video.

    Args:
        file_path (str): Path to the local video file.

    Returns:
        bool: True if the file is a valid video, False otherwise.
    """
    try:
        # Step 1: Check if the file exists and is a file
        if not os.path.exists(file_path):
            logging.info(f"File does not exist: {file_path}")
            return False
        if not os.path.isfile(file_path):
            logging.info(f"Path is not a file: {file_path}")
            return False

        # Step 2: Open the video with OpenCV
        video = cv2.VideoCapture(file_path)
        if not video.isOpened():
            logging.info(f"Cannot open video file: {file_path}")
            video.release()
            return False

        # Step 3: Check if at least one frame can be read
        ret, frame = video.read()
        if not ret:
            logging.info(f"Video is empty or corrupted: {file_path}")
            video.release()
            return False

        # Optional: Check video properties (e.g., frame count > 0)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            logging.info(f"Video has no frames: {file_path}")
            video.release()
            return False

        video.release()
        logging.info(f"Valid video file found: {file_path}")
        return True

    except Exception as e:
        logging.info(f"Error validating video file: {e}")
        return False
    finally:
        # Ensure video is released even on error
        if "video" in locals():
            video.release()
