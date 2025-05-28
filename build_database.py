import json
import os
import random
from itertools import chain
from typing import Generator, Tuple

from loguru import logger
from tqdm import tqdm

from src.milvus import MilvusDatabase, insert_task_output_to_milvus
from src.model import MultimodalEmbeddingModel
from src.schemas.base import VideoMetadata
from src.schemas.input import TaskInput

VIDEO_FETCH_AND_TRIM_FOLDER_PATH = "video-fetch-and-trim"
DB_URL = os.environ.get("DB_URL", "milvus_embedding.db")
VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")


def get_videos_and_descriptions_from_urls() -> (
    Generator[Tuple[VideoMetadata, str], None, None]
):
    sample_video_urls = [
        "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    ]

    sample_descriptions = [
        "A short, fiery promo with bold text and intense music.",
        "Quick action clip featuring a daring escape scene.",
        "Dramatic meltdown montage with fast cuts and chaos.",
    ]
    for source, description in zip(sample_video_urls, sample_descriptions):
        yield (
            {
                "category": "sample_category",
                "description": description,
                "length": 10,  # fake length
            },
            source,
        )


def get_videos_and_descriptions() -> Generator[Tuple[VideoMetadata, str], None, None]:
    metadata_folder_path = os.path.join(VIDEO_FETCH_AND_TRIM_FOLDER_PATH, "metadata")
    videos_folder_path = os.path.join(VIDEO_FETCH_AND_TRIM_FOLDER_PATH, "videos")
    video_files = [
        os.path.join(videos_folder_path, file)
        for file in os.listdir(videos_folder_path)
        if file.endswith(".mp4")
        # and file.startswith("news & politics") # [DEBUG] hardcoded for testing -> remove later
    ]

    # [Note] hardcoded for testing -> remove later
    video_files = random.choices(video_files, k=10)

    for video_file in tqdm(video_files):
        metadata_file_name = os.path.basename(video_file)
        metadata_file = os.path.join(
            metadata_folder_path, f"{os.path.splitext(metadata_file_name)[0]}.json"
        )
        if not os.path.exists(metadata_file):
            continue

        with open(metadata_file, "r") as file:
            metadata = json.load(file)

        yield (
            {
                "category": metadata["category"],
                "description": metadata["description"],
                "length": metadata["length"],
            },
            video_file,
        )


def basic_build_database(milvus: MilvusDatabase):
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Define sample input data (video + description pairs).
    # For video, you can either use URL or local file, it will be auto-detected).
    # In practical, the data is downloaded from a large data source instead.
    loader_ = get_videos_and_descriptions_from_urls()

    inputs = [
        TaskInput(
            video=source,
            text=metadata["description"],
        )
        for metadata, source in loader_
    ]

    # Calculate embeddings
    outputs = [model.generate_embedding(input) for input in inputs]

    # Store data into vector database Milvus. The following code will create
    # milvus database in Lite version, create two collections named
    # "video_embedding" and "text_embedding to store embeddings"

    # Insert data into collections
    for output in outputs:
        insert_task_output_to_milvus(
            milvus, output, VIDEO_COLLECTION_NAME, TEXT_COLLECTION_NAME
        )

    logger.info("Build database successfully")


def main_build_database(milvus: MilvusDatabase):
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Store data into vector database Milvus. The following code will create
    # milvus database in Lite version, create two collections named
    # "video_embedding" and "text_embedding to store embeddings"

    # Define input data (video + description pairs).
    loader_ = get_videos_and_descriptions()
    loader_url_ = []  # get_videos_and_descriptions_from_urls()

    for metadata, video_path in chain(loader_, loader_url_):
        # Define input data (video + description pairs).
        input_ = TaskInput(
            video=video_path,
            text=metadata["description"],
        )

        try:
            # Calculate embeddings
            output = model.generate_embedding(input_)
        except Exception as e:
            logger.info(f"Error processing video {video_path}: {e}")
            continue

        # Insert data into collections
        insert_task_output_to_milvus(
            milvus, output, VIDEO_COLLECTION_NAME, TEXT_COLLECTION_NAME
        )

    logger.info("Build database successfully")


if __name__ == "__main__":
    milvus = MilvusDatabase(DB_URL)
    FORCE = False
    if FORCE or not milvus.milvus_client.has_collection(
        collection_name=VIDEO_COLLECTION_NAME
    ):
        milvus.create_collection(VIDEO_COLLECTION_NAME)
    if FORCE or not milvus.milvus_client.has_collection(
        collection_name=TEXT_COLLECTION_NAME
    ):
        milvus.create_collection(TEXT_COLLECTION_NAME)
    main_build_database(milvus)
