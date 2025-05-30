import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from loguru import logger
from pydantic import BaseModel

# from src.fastapi.client_example import download_file
from src.fastapi.client_example import download_file
from src.milvus import MilvusDatabase
from src.model import MultimodalEmbeddingModel
from src.schemas.input import TaskInput

# Load multiple DB URLs from environment
DB_URLs = os.environ.get("DB_URLs", "http://localhost:19530").split(",")

VIDEO_COLLECTION_NAME = os.environ.get("VIDEO_COLLECTION_NAME", "video_embedding")
TEXT_COLLECTION_NAME = os.environ.get("TEXT_COLLECTION_NAME", "text_embedding")

logger.info(f"Retrieving data from Milvus instances: {DB_URLs}")

model = MultimodalEmbeddingModel()
milvus_instances = [MilvusDatabase(url.strip()) for url in DB_URLs]

sample_videos = [
    "video-fetch-and-trim/videos/education_0.mp4",  # local
    "video-fetch-and-trim/videos/education_2.mp4",  # local
    "video-fetch-and-trim/videos/news & politics_0.mp4",  # local
    "video-fetch-and-trim/videos/news & politics_1.mp4",  # local
]


class VideoAttributes(BaseModel):
    video_path: str
    video_embedding: List[float]
    uri: str


def main(video_url: str, video_embedding: List[float]) -> List[VideoAttributes]:
    input_ = TaskInput(
        video=video_url,
        video_embedding=video_embedding,
        text=None,
    )
    results = []

    def query_from_instance(milvus_instance):
        res = model.retrieve_similarity_from_milvus(
            input_,
            milvus_instance,
            VIDEO_COLLECTION_NAME,
            TEXT_COLLECTION_NAME,
            limit=30,
        )
        return milvus_instance, res

    with ThreadPoolExecutor(max_workers=len(milvus_instances)) as executor:
        futures = [executor.submit(query_from_instance, m) for m in milvus_instances]
        for future in as_completed(futures):
            try:
                milvus_ins, res = future.result()
                res.milvus_uri = milvus_ins.uri
                for i in range(len(res.videos)):
                    if res.milvus_uri != os.environ.get("DB_URL"):
                        # TODO, request to download here
                        download_file(
                            res.milvus_uri,
                            os.path.basename(res.videos[i]),
                            # "download/" + res.videos[i], # for individual testing
                            res.videos[i],  # for distributed testing
                        )
                    video_attributes = VideoAttributes(
                        video_path=res.videos[i],
                        video_embedding=res.video_embeddings[i],
                        uri=res.milvus_uri,
                    )
                    results.append({video_attributes.video_path: video_attributes})
            except Exception as e:
                logger.error(f"Query failed from instance: {e}")

    logger.info(
        f"Retrieved {len(results)} videos for {video_url}: {[list(res.keys())[0] for res in results]}"
    )

    unique_dict: Dict[str, VideoAttributes] = {}
    for item in results:
        for key, value in item.items():
            # if key == video_url:
            #     continue
            if key not in unique_dict:
                unique_dict[key] = value

    logger.info(
        f"Retrieved {len(unique_dict)} unique videos from Milvus instances: {DB_URLs}"
    )
    video_list = list(unique_dict.values())
    return video_list


def init(n_videos: int) -> List[VideoAttributes | None]:
    """Return list of trending videos"""
    results: List[Dict[str, VideoAttributes]] = []

    def fetch_from_instance(milvus_instance: MilvusDatabase, url):
        return url, milvus_instance.query(
            collection_name=VIDEO_COLLECTION_NAME,
            limit=30,
            output_fields=["video", "embeddings_float"],
        )

    with ThreadPoolExecutor(max_workers=len(milvus_instances)) as executor:
        futures = [
            executor.submit(fetch_from_instance, m, url)
            for m, url in zip(milvus_instances, DB_URLs)
        ]
        for future in as_completed(futures):
            try:
                url, res = future.result()
                logger.info(f"Fetched {len(res)} videos from {url}")
                for video in res:
                    # TODO, request to download here
                    if url != os.environ.get("DB_URL"):
                        download_file(
                            url,
                            os.path.basename(video["video"]),
                            # "download/" + video["video"], # for individual testing
                            video["video"],  # for distributed testing
                        )
                    video_attributes = VideoAttributes(
                        video_path=video["video"],
                        video_embedding=video["embeddings_float"],
                        uri=url,
                    )
                    results.append({video_attributes.video_path: video_attributes})
            except Exception as e:
                logger.error(f"Init query failed from instance: {e}")

    unique_dict: Dict[str, VideoAttributes] = {}
    for item in results:
        for key, value in item.items():
            if key not in unique_dict:
                unique_dict[key] = value

    logger.info(
        f"Retrieved {len(unique_dict)} unique videos from Milvus instances: {DB_URLs}"
    )
    video_list = list(unique_dict.values())
    # Pad with None if not enough videos
    logger.info(
        f"There are/is {len([None] * abs(max(n_videos - len(video_list), 0)))} lack of videos, padding with None"
    )
    video_list = video_list[:n_videos] + [None] * abs(
        max(n_videos - len(video_list), 0)
    )
    return video_list
