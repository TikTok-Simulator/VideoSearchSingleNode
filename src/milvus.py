from pymilvus import MilvusClient
    
milvus_client = MilvusClient("milvus_twelvelabs_demo.db")

print("Successfully connected to Milvus")


collection_name = "twelvelabs_demo_collection"

if milvus_client.has_collection(collection_name=collection_name):
    milvus_client.drop_collection(collection_name=collection_name)

milvus_client.create_collection(
    collection_name=collection_name,
    dimension=1024  # The dimension of the Twelve Labs embeddings
)

print(f"Collection '{collection_name}' created successfully")
