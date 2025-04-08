from src.schemas.input import TaskInput
from src.model import MultimodalEmbeddingModel
from src.milvus import MilvusDatabase, insert_task_output_to_milvus


if __name__ == "__main__":
    # Define embedding model
    model = MultimodalEmbeddingModel()

    # Define sample input data (video + description pairs).
    # For video, you can either use URL or local file, it will be auto-detected).
    # In practical, the data is downloaded from a large data source instead.
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
    inputs = [
        TaskInput(
            video=source,
            text=description,
        )
        for source, description in zip(sample_video_urls, sample_descriptions)
    ]

    # Calculate embeddings
    outputs = [model.generate_embedding(input) for input in inputs]

    # Store data into vector database Milvus. The following code will create
    # milvus database in Lite version, create two collections named
    # "video_embedding" and "text_embedding to store embeddings"
    milvus = MilvusDatabase("milvus_embedding.db")
    video_collection_name, text_collection_name = "video_embedding", "text_embedding"
    milvus.create_collection(video_collection_name)
    milvus.create_collection(text_collection_name)

    # Insert data into collections
    for output in outputs:
        insert_task_output_to_milvus(
            milvus, output, video_collection_name, text_collection_name
        )

    print("Build database successfully")
