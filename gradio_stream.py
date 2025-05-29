import gradio as gr
import cv2
import uuid

SUBSAMPLE = 2


def process_video(video_path):
    cap = cv2.VideoCapture(
        filename="https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_30mb.mp4"
    )
    fps = int(cap.get(cv2.CAP_PROP_FPS)) // SUBSAMPLE  # Giảm tốc độ khung hình
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_codec = cv2.VideoWriter.fourcc(*"mp4v")  # Codec for MP4 format
    output_video_name = f"output_{uuid.uuid4()}.mp4"
    output_video = cv2.VideoWriter(output_video_name, video_codec, fps, (width, height))

    n_frames = 0
    batch = []
    ret, frame = cap.read()
    while ret:
        if n_frames % SUBSAMPLE == 0:
            batch.append(frame)
        if len(batch) == SUBSAMPLE * fps:
            for frame in batch:
                output_video.write(frame)
            batch = []
            output_video.release()
            yield output_video_name
            output_video = cv2.VideoWriter(
                output_video_name, video_codec, fps, (width, height)
            )  # type: ignore

        ret, frame = cap.read()
        n_frames += 1

    cap.release()
    output_video.release()


with gr.Blocks() as demo:
    video_component = gr.Video(
        label="Downloaded Video",
        autoplay=True,
        loop=False,
        interactive=False,
        streaming=True,
    )

    gr.Button("Download and Show Video").click(
        fn=process_video,
        outputs=video_component,
    )

demo.launch(share=True)
