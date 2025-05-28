import os
from loguru import logger
from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase

DB_URL = os.environ.get("DB_URL", "milvus_embedding.db")
VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")

logger.info(f"Retrieving data from Milvus database: {DB_URL}")

model = MultimodalEmbeddingModel()
milvus = MilvusDatabase(DB_URL)

sample_videos = [
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",# too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",# too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",# too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4", # too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4", # too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",  # too long :v
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",  # 15s
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",  # 15s
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",  # 15s
    # "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",  # 15s
    "video-fetch-and-trim/videos/education_0.mp4",  # local
    "video-fetch-and-trim/videos/education_2.mp4",  # local
    "video-fetch-and-trim/videos/news & politics_0.mp4",  # local
    "video-fetch-and-trim/videos/news & politics_1.mp4",  # local
]


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


def init(n_videos: int):
    """Return list of trending videos"""
    results = milvus.query(
        collection_name=VIDEO_COLLECTION_NAME, limit=20, output_fields=["video"]
    )
    video_list = [res["video"] for res in results]

    # TODO fix it: why it duplicate here
    video_list = list(dict.fromkeys(video_list))  # remove duplicate
    video_list = video_list[:n_videos] + [None] * abs(
        n_videos - len(video_list)
    )  # pad with None if not enough videos
    return video_list
    # return sample_videos[:n_videos]
