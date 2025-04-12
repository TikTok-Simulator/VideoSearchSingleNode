import gradio as gr

with gr.Blocks() as demo:
    gr.Video(
        value="TearsOfSteel.mp4",
        label="Local Streaming Video",
        autoplay=True,
        loop=False,
        interactive=False,
    )

demo.launch()
