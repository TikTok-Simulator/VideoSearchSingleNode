import gradio as gr
import requests


# ------------------------------------------------------------------------------------------
# This streaming method does not work!!!
# ------------------------------------------------------------------------------------------

SUBSAMPLE = 2


def process_video(video_path):
    response = requests.get(
        "https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_30mb.mp4",
        stream=True,
    )
    if response.status_code == 200:
        with open("chunk_video.mp4", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    yield "chunk_video.mp4"


with gr.Blocks() as demo:
    video_component = gr.Video(
        label="Streaming Video",
        autoplay=True,
        loop=False,
        interactive=False,
        streaming=True,
        # include_audio=True,
    )

    gr.Button("Stream Video").click(
        fn=process_video,
        outputs=video_component,
    )

demo.launch(share=True)
