import os
from loguru import logger
from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase

DB_URL = os.environ.get("DB_URL", "milvus_embedding.db")
VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")

logger.info(f"Retrieving data from Milvus database: {DB_URL}")


def basic_run(milvus: MilvusDatabase):
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Define sample query data (video + description)
    # sample_video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    sample_video_file = "video-fetch-and-trim/videos/lifestyle_0.mp4"  # Can use wget to download the URL as local file
    sample_description = "The video tutorial demonstrates the preparation of Vendakka MoruCurry showcasing ingredients and cooking steps."
    input_ = TaskInput(
        video=sample_video_file,
        text=sample_description,
    )

    # Retrieve a video
    results = model.retrieve_similarity_from_milvus(
        input_, milvus, VIDEO_COLLECTION_NAME, TEXT_COLLECTION_NAME, limit=3
    )

    print("Retrieval results:\n", results)


def main_run():
    # TODO
    pass


if __name__ == "__main__":
    milvus = MilvusDatabase(DB_URL)
    basic_run(milvus)
