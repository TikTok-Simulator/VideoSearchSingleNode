import os
import logging
from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase

DB_URL = os.environ.get("DB_URL", "milvus_embedding.db")
VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")

logging.info("Retrieving data from Milvus database: %s", DB_URL)

model = MultimodalEmbeddingModel()
milvus = MilvusDatabase(DB_URL)


def main(video_url: str):
    # Define embedding model
    global model, milvus

    input_ = TaskInput(
        video=video_url,
        text=None,
    )

    # Retrieve a video
    results = model.retrieve_similarity_from_milvus(
        input_, milvus, VIDEO_COLLECTION_NAME, TEXT_COLLECTION_NAME, limit=10
    )

    return results
