from typing import Dict, List, Union

from pymilvus import MilvusClient
    
from .schemas.output import TaskOutput


class MilvusDatabase:
    def __init__(self, db_name: str):
        self.milvus_client = self._create_database(db_name)
    
    def _create_database(self, db_name: str = "milvus_twelvelabs_demo.db") -> MilvusClient:
        # This is a quickstart to create a local vector database
        milvus_client = MilvusClient(db_name)

        print("Successfully connected to Milvus")
        return milvus_client

    def create_collection(
        self,
        collection_name: str = "twelvelabs_demo_collection"
    ):
        if self.milvus_client.has_collection(collection_name=collection_name):
            self.milvus_client.drop_collection(collection_name=collection_name)

        self.milvus_client.create_collection(
            collection_name=collection_name,
            dimension=1024,  # The dimension of the Twelve Labs embeddings
            auto_id=True,
            vector_field_name="embeddings_float"
        )

        print(f"Collection '{collection_name}' created successfully")


    def insert(
        self, 
        collection_name: str, 
        data: Union[Dict, List[Dict]]
    ):
        insert_result = self.milvus_client.insert(collection_name=collection_name, data=data)
        return insert_result


def insert_task_output_to_milvus(
    milvus: MilvusDatabase,
    task_output: TaskOutput,
    video_collection_name: str = "video_embedding",
    text_collection_name: str = "text_embedding",
):
    task_output_data = task_output.model_dump()
    
    video_data = task_output_data["video_embeddings"]
    res = milvus.insert(video_collection_name, video_data)
    video_ids = res["ids"]
    print(f"Inserted video embeddings with IDs: {video_ids}")
    
    if task_output_data["text_embedding"]:
        text_data = task_output_data["text_embedding"]

        res = milvus.insert(text_collection_name, text_data)
        text_ids = res["ids"]
        print(f"Inserted text embeddings with IDs: {text_ids}")
    