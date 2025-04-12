import random
import gradio as gr

video_list = [
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",# too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",# too long :v
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",# too long :v
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4", # too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4", # too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",  # too long :v
]

N_VIDEOS = 4

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


def select_video(selected_video: str):
    """Update the current index based on the selected video and return that video."""
    global current_index
    try:
        current_index = video_list.index(selected_video)
    except ValueError:
        current_index = 0
    return video_list[current_index]


def get_next_video():
    """Cycle to the next video and return it."""
    global current_index
    current_index = (current_index + 1) % len(video_list)
    return video_list[current_index]


def update_display_video(video_url: str):
    return gr.update(elem_id="video-display", value=video_url)


def retrieve_related_videos(video_url: str):
    global video_list
    # Shuffle video_list
    video_list = random.sample(video_list, len(video_list))
    indices = random.sample(range(N_VIDEOS), N_VIDEOS)
    return [
        gr.update(elem_id=f"recommended-video-{i}", value=video_list[vi])
        for i, vi in enumerate(indices)
    ]


# def stream_video(video_path):
#     # Stream logic here
#     yield video_path


with gr.Blocks(js=custom_js) as demo:
    gr.Markdown("## TikTok2 Simulator Recommended Videos")

    with gr.Row():
        video_display = gr.Video(
            value=video_list[0],
            label="Video Player",
            autoplay=True,
            loop=True,
            interactive=False,
            elem_id="video-display",
            # streaming=True,  # TODO
        )

    # Button to load the next video from the list.
    next_button = gr.Button("▶ Next")

    gr.Button("▶ Play all recommended videos", elem_id="play-all-button")

    recommended_videos_display = []
    with gr.Row():
        for i, video_path in enumerate(video_list[:N_VIDEOS]):
            with gr.Column():
                video_text_box = gr.Textbox(value=video_path, visible=False)
                recommended_videos_display += [
                    gr.Video(
                        elem_id=f"recommended-video-{i}",
                        value=video_path,
                        label=None,
                        autoplay=True,
                        loop=True,
                        interactive=False,
                        show_label=False,
                        # streaming=True,  # TODO
                    )
                ]
                gr.Button(f"▶ Video {i + 1}", elem_id=f"select-btn-{i}").click(
                    fn=update_display_video,
                    inputs=[video_text_box],
                    outputs=video_display,
                )

    # When the next button is clicked, display the next video.
    next_button.click(fn=get_next_video, outputs=video_display)
    video_display.change(
        fn=retrieve_related_videos,
        inputs=[video_display],
        outputs=recommended_videos_display,
    )

demo.launch()
