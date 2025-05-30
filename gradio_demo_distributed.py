import os
from loguru import logger
import gradio as gr
from typing import Dict
from gradio_main_distributed import main, init

# from src.schemas.output import RetrievalOutput
from gradio_main_distributed import VideoAttributes

# Paths can be a list of strings or pathlib.Path objects
# corresponding to filenames or directories.
# https://www.gradio.app/docs/gradio/set_static_paths
# !Important, if you do not define like that, a file will be located in a temp and uncontrolled path
gr.set_static_paths(paths=["video-fetch-and-trim/videos/"])


N_SIMILAR_VIDEOS = 4
video_attributes_list = init(
    n_videos=1 + N_SIMILAR_VIDEOS
)  # the main and recommended videos
recommended_video_list = [
    v.video_path for v in video_attributes_list[1:] if v is not None
]
if video_attributes_list is None or len(video_attributes_list) == 0:
    raise ValueError(
        "No video attributes found. Please ensure that the video paths are correct."
    )
if any(v is None for v in video_attributes_list):
    raise ValueError(
        "Some video attributes are None. Please ensure that all video paths are valid."
    )

logger.info(
    f"Trending videos: {[v.video_path for v in video_attributes_list if v is not None]}"
)

# This JS will be injected once and run when the app loads
custom_js = """
() => {
    const playAll = () => {
        const videos = document.querySelectorAll("video");
        videos.forEach(v => {
            v.play().catch(err => console.warn("Video play failed:", err));
        });
    };

    // Add global listener for button with specific ID
    setTimeout(() => {
        const btn = document.getElementById("play-all-button");
        if (btn) {
            btn.addEventListener("click", playAll);
        }
    }, 500);
}
"""

# Global index to track the current video
current_index = 0


# def select_video(selected_video: str):
#     """Update the current index based on the selected video and return that video."""
#     global current_index
#     try:
#         current_index = video_attributes_list.index(selected_video)
#     except ValueError:
#         current_index = 0
#     return video_attributes_list[current_index]


def get_next_video():
    """Cycle to the next video and return it."""
    global recommended_video_list
    return recommended_video_list[0]


def update_display_video(video_url: str):
    return video_url


def update_category(video_url: str):
    """Update the category label based on the video URL."""
    category = os.path.basename(video_url).split(".")[0].split("_")[0]
    return category


def retrieve_related_videos(
    local_video_path: str, embedding_dict: Dict[str, VideoAttributes]
):  # -> embedding_dict, recommended_videos_display: List[gr.Video]:
    global current_index, recommended_video_list

    """Retrieve related videos based on the current video and update the embedding dictionary."""
    if local_video_path is None or local_video_path == "":
        gr.Error("No video path provided.")
    if local_video_path not in embedding_dict:
        gr.Error(f"Video path {local_video_path} not found in embedding dictionary.")

    retrieved_videos = main(
        video_url=local_video_path,
        video_embedding=embedding_dict[local_video_path].video_embedding,
    )
    for retrieved_video in retrieved_videos:
        if retrieved_video.video_path not in embedding_dict:
            embedding_dict[retrieved_video.video_path] = retrieved_video

    # Update the current index to the first video in the retrieved list
    current_index = 0

    # Update the video list with the new retrieved videos
    recommended_video_list = [
        v.video_path for v in retrieved_videos[:N_SIMILAR_VIDEOS] if v is not None
    ]
    logger.info(
        f"Retrieved videos: {[v.video_path for v in retrieved_videos if v is not None]} for {local_video_path}"
    )
    return [embedding_dict] + recommended_video_list


with gr.Blocks(js=custom_js) as demo:
    gr.Markdown("## TikTok2 Simulator Recommended Videos")
    embedding_store = gr.State({
        v.video_path: v for v in video_attributes_list if v is not None
    })  ####### !IMPORTANT. This is in memory vector database ##########################
    with gr.Row():
        video_display = gr.Video(
            value=video_attributes_list[0].video_path,  # type:ignore
            label="Video Player",
            autoplay=True,
            loop=True,
            elem_id="video-display",
        )

    # Button to load the next video from the list.

    with gr.Row():
        text_box_display = gr.Textbox(
            label="Category",
            value=os.path.basename(video_attributes_list[0].video_path)  # type:ignore
            .split(".")[0]
            .split("_")[0],
            elem_id="video-label-display",
        )
        next_button = gr.Button("▶ Next")
        video_display.change(
            update_category,
            inputs=[video_display],
            outputs=[text_box_display],
        )

    # gr.Button("▶ Play all recommended videos", elem_id="play-all-button")

    recommended_videos_display = []
    with gr.Row():
        for i, video_attributes in enumerate(video_attributes_list[1:]):
            with gr.Column():
                # do not create gr.Video individually, it will be deleted after for loop
                recommended_video = gr.Video(
                    elem_id=f"recommended-video-{i}",
                    value=video_attributes.video_path,  # type:ignore
                    label=None,
                    autoplay=False,
                    loop=True,
                    interactive=False,
                    show_label=False,
                )
                recommended_videos_display += [recommended_video]
                with gr.Row():
                    text_box = gr.Textbox(
                        label="Category",
                        value=os.path.basename(video_attributes.video_path)  # type:ignore
                        .split(".")[0]
                        .split("_")[0],
                        elem_id=f"video-label-{i}",
                    )
                    recommended_video.change(
                        update_category,
                        inputs=[recommended_videos_display[-1]],
                        outputs=[text_box],
                    )
                    gr.Button(f"▶ Video {i + 1}", elem_id=f"select-btn-{i}").click(
                        fn=update_display_video,
                        inputs=[recommended_videos_display[-1]],
                        outputs=video_display,
                    )

    # play_button.click(
    #     fn=select_the_first_video,
    #     outputs=video_display,
    # )

    # When the next button is clicked, display the next video.
    next_button.click(
        fn=get_next_video,
        outputs=[video_display],
    )
    video_display.change(
        fn=retrieve_related_videos,
        inputs=[video_display, embedding_store],
        outputs=[embedding_store] + recommended_videos_display,
    )

if __name__ == "__main__":
    demo.launch()
