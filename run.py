from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase, insert_task_output_to_milvus


if __name__ == "__main__":
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Define sample input data (video + description)
    sample_video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    sample_video_file = "static/ForBiggerBlazes.mp4"
    sample_description = """"For Bigger Blazes" is a short promotional video from Google's collection of sample media, hosted on their Video Bucket (Google Cloud Storage)."""

    # Calculate embedding
    inputs = [
        TaskInput(
            video=source,
            text=sample_description,
        )
        for source in [sample_video_url, sample_video_file]
    ]
    outputs = [model.generate_embedding(input) for input in inputs]

    # Store data into vector database Milvus
    milvus = MilvusDatabase("milvus_embedding.db")
    video_collection_name, text_collection_name = "video_embedding", "text_embedding"
    milvus.create_collection(video_collection_name)
    milvus.create_collection(text_collection_name)

    for output in outputs:
        insert_task_output_to_milvus(
            milvus, output, video_collection_name, text_collection_name
        )
