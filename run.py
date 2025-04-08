from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase


if __name__ == "__main__":
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Define sample query data (video + description)
    # sample_video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    sample_video_file = (
        "static/ForBiggerFun.mp4"  # Can use wget to download the URL as local file
    )
    sample_description = "Fast-paced clip showcasing a thrilling, fun chase scene."
    input_ = TaskInput(
        video=sample_video_file,
        text=sample_description,
    )

    # Store data into vector database Milvus
    milvus = MilvusDatabase("milvus_embedding.db")
    video_collection_name, text_collection_name = "video_embedding", "text_embedding"

    # Retrieve a video
    results = model.retrieve_similarity_from_milvus(
        input_, milvus, video_collection_name, text_collection_name, limit=1
    )

    print("Retrieval results:\n", results)
