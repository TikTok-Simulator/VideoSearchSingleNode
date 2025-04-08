import logging
from typing import Dict, List, Tuple, Optional

from twelvelabs.models.embed import EmbeddingsTask

from .core import model_name, twelvelabs_client
from ..utils.process_video import upscale_video_resolution, get_video_duration


class VideoEmbeddingModel:
    def __init__(self):
        self.twelvelabs_client = twelvelabs_client

    def generate_embedding_url(
        self, video_url: str
    ) -> Tuple[List[Dict], EmbeddingsTask]:
        """
        Generate embeddings for a given video URL using the Twelve Labs API.

        This function creates an embedding task for the specified video URL using
        the Marengo-retrieval-2.7 engine. It monitors the task progress and waits
        for completion. Once done, it retrieves the task result and extracts the
        embeddings along with their associated metadata.

        Args:
            video_url (str): The URL of the video to generate embeddings for.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries, where each dictionary contains:
                    - 'embedding': The embedding vector as a list of floats.
                    - 'start_offset_sec': The start time of the segment in seconds.
                    - 'end_offset_sec': The end time of the segment in seconds.
                    - 'embedding_scope': The scope of the embedding (e.g., 'shot', 'scene').
                2. EmbeddingsTask: The complete task result object from Twelve Labs API.

        Raises:
            Any exceptions raised by the Twelve Labs API during task creation,
            execution, or retrieval.
        """

        # Create an embedding task
        video_duration = get_video_duration(video_url)

        if not video_duration:
            task = self.twelvelabs_client.embed.task.create(
                model_name=model_name,
                video_url=video_url,
                video_embedding_scopes=["clip", "video"],
            )
        else:
            task = self.twelvelabs_client.embed.task.create(
                model_name=model_name,
                video_url=video_url,
                video_start_offset_sec=0,
                video_end_offset_sec=video_duration,
                video_embedding_scopes=["clip", "video"],
            )

        logging.info(
            f"Created task: id={task.id} model_name={task.model_name} status={task.status}"
        )

        # Define a callback function to monitor task progress
        def on_task_update(task: EmbeddingsTask):
            logging.info(f"  Status={task.status}")

        # Wait for the task to complete
        status = task.wait_for_done(sleep_interval=2, callback=on_task_update)
        logging.info(f"Embedding done: {status}")

        # Retrieve the task result
        task_result = self.twelvelabs_client.embed.task.retrieve(task.id)

        # Extract and return the embeddings
        embeddings = []
        for v in task_result.video_embedding.segments:
            embeddings.append(
                {
                    "embeddings_float": v.embeddings_float,
                    "start_offset_sec": v.start_offset_sec,
                    "end_offset_sec": v.end_offset_sec,
                    "embedding_scope": v.embedding_scope,
                }
            )

        return embeddings, task_result

    def generate_embedding_file(
        self, video_file: str
    ) -> Tuple[List[Dict], EmbeddingsTask]:
        """
        Generate embeddings for a given video file using the Twelve Labs API.

        This function creates an embedding task for the specified video file path using
        the Marengo-retrieval-2.7 engine. It monitors the task progress and waits
        for completion. Once done, it retrieves the task result and extracts the
        embeddings along with their associated metadata.

        Args:
            video_file (str): The path of the video to generate embeddings for.

        Returns:
            tuple: A tuple containing two elements:
                1. list: A list of dictionaries, where each dictionary contains:
                    - 'embedding': The embedding vector as a list of floats.
                    - 'start_offset_sec': The start time of the segment in seconds.
                    - 'end_offset_sec': The end time of the segment in seconds.
                    - 'embedding_scope': The scope of the embedding (e.g., 'shot', 'scene').
                2. EmbeddingsTaskResult: The complete task result object from Twelve Labs API.

        Raises:
            Any exceptions raised by the Twelve Labs API during task creation,
            execution, or retrieval.

        Notes:
            - Video resolution: Must be at least 360x360 and must not exceed 3840x2160.
            - Aspect ratio: Must be one of 1:1, 4:3, 4:5, 5:4, 16:9, or 9:16.
            - Video and audio formats: The video files must be encoded in the video and audio formats listed on the FFmpeg Formats Documentation
            page. For videos in other formats, contact us at support@twelvelabs.io.
            - Duration: Must be between 4 seconds and 2 hours (7,200s).
            - File size: Must not exceed 2 GB.
        """

        # Create an embedding task
        video_duration = get_video_duration(video_file)

        if not video_duration:
            task = self.twelvelabs_client.embed.task.create(
                model_name=model_name,
                video_file=video_file,
                video_embedding_scopes=["clip", "video"],
            )
        else:
            task = self.twelvelabs_client.embed.task.create(
                model_name=model_name,
                video_file=video_file,
                video_start_offset_sec=0,
                video_end_offset_sec=video_duration,
                video_embedding_scopes=["clip", "video"],
            )

        logging.info(
            f"Created task: id={task.id} model_name={task.model_name} status={task.status}"
        )

        # Define a callback function to monitor task progress
        def on_task_update(task: EmbeddingsTask):
            logging.info(f"  Status={task.status}")

        # Wait for the task to complete
        status = task.wait_for_done(sleep_interval=2, callback=on_task_update)
        logging.info(f"Embedding done: {status}")

        # Retrieve the task result
        task_result = self.twelvelabs_client.embed.task.retrieve(task.id)

        # Extract and return the embeddings
        embeddings = []
        for v in task_result.video_embedding.segments:
            embeddings.append(
                {
                    "embeddings_float": v.embeddings_float,
                    "start_offset_sec": v.start_offset_sec,
                    "end_offset_sec": v.end_offset_sec,
                    "embedding_scope": v.embedding_scope,
                }
            )

        return embeddings, task_result

    def preprocess_video(self, video_url: str) -> str:
        return upscale_video_resolution(video_url)
