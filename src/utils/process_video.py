import cv2
import urllib.request
import os


def upscale_video_resolution(
    video_url: str, output_dir_relative: str = "../static/processed_file"
) -> str:
    # Download the video from the URL to a temporary file
    temp_path = "temp_video.mp4"
    urllib.request.urlretrieve(video_url, temp_path)

    # Open the video
    video = cv2.VideoCapture(temp_path)
    if not video.isOpened():
        raise ValueError("Could not open video from URL")

    # Get original video properties
    original_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    # Define output_path automatically
    current_dir = os.path.dirname(__file__)
    output_dir = os.path.join(current_dir, output_dir_relative)
    os.makedirs(output_dir, exist_ok=True)

    output_name = os.path.basename(
        video_url.split("?")[0]
    )  # Remove query params if any
    if not output_name.lower().endswith(".mp4"):  # Ensure it has a valid extension
        output_name += ".mp4"

    output_path = os.path.join(output_dir, output_name)

    # Check if upscaling is needed
    if original_width >= 360 and original_height >= 360:
        print(
            "Video resolution is already sufficient (>= 360x360). No upscaling needed."
        )
        video.release()
        os.rename(temp_path, output_path)  # Just move the original file
        return output_path

    # Calculate the scaling factor to make the smaller dimension at least 360
    aspect_ratio = original_width / original_height
    if original_width < 360:
        target_width = 360
        target_height = int(target_width / aspect_ratio)
    elif original_height < 360:
        target_height = 360
        target_width = int(target_height * aspect_ratio)
    else:
        target_width, target_height = (
            original_width,
            original_height,
        )  # Shouldn't hit this due to prior check

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    # Check if VideoWriter is opened successfully
    if not out.isOpened():
        video.release()
        raise ValueError(
            f"Failed to open VideoWriter with codec 'mp4v' at {output_path}"
        )

    # Process each frame
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        # Resize the frame to the new resolution
        resized_frame = cv2.resize(
            frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR
        )
        out.write(resized_frame)

    # Release resources
    video.release()
    out.release()
    cv2.destroyAllWindows()

    # Clean up temporary file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    print(
        f"Video upscaled to {target_width}x{target_height} and saved to {output_path}"
    )
    return output_path
