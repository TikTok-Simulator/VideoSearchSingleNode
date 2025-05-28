import json
import os
import random
from itertools import chain
from typing import Generator, Tuple

from loguru import logger
from tqdm import tqdm
import yaml  # Add YAML import

from src.milvus import MilvusDatabase, insert_task_output_to_milvus
from src.model import MultimodalEmbeddingModel
from src.schemas.base import VideoMetadata
from src.schemas.input import TaskInput

VIDEO_FETCH_AND_TRIM_FOLDER_PATH = "video-fetch-and-trim"
DB_URL = os.environ.get("DB_URL", "milvus_embedding.db")
VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")


def load_config(config_path: str):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_videos_and_descriptions(
    config: dict,
) -> Generator[Tuple[VideoMetadata, str], None, None]:
    metadata_folder_path = os.path.join(config["base_dir"], config["metadata_path"])
    videos_folder_path = os.path.join(config["base_dir"], config["videos_path"])
    video_files = [
        os.path.join(videos_folder_path, file)
        for file in os.listdir(videos_folder_path)
        if file.endswith(".mp4")
    ]

    # [Note] hardcoded for testing -> remove later
    if os.environ.get("ENVIRONMENT") == "test":
        video_files = random.choices(video_files, k=min(10, len(video_files)))

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


def main_build_database(milvus: MilvusDatabase):
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Store data into vector database Milvus. The following code will create
    # milvus database in Lite version, create two collections named
    # "video_embedding" and "text_embedding to store embeddings"

    # Define input data (video + description pairs).
    loader_ = get_videos_and_descriptions(config)

    for metadata, video_path in chain(loader_):
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
    import argparse

    parser = argparse.ArgumentParser(description="Build video embedding database.")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to the YAML configuration file."
    )
    args = parser.parse_args()

    config = load_config(args.config)

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
