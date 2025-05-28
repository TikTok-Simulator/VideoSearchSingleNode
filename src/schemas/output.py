from typing import List, Optional
from pydantic import BaseModel, Field


class VideoEmbedding(BaseModel):
    video: str
    embeddings_float: List[float] = Field(default_factory=list)
    embedding_scope: str
    start_offset_sec: float
    end_offset_sec: float


class TextEmbedding(BaseModel):
    text: str
    embeddings_float: List[float] = Field(default_factory=list)


class TaskOutput(BaseModel):
    video_embeddings: List[VideoEmbedding] = Field(default_factory=list)
    text_embedding: Optional[TextEmbedding] = None


class RetrievalOutput(BaseModel):
    videos: List[str] = Field(default_factory=list)
    text_list: List[str] = Field(default=[])
    milvus_uri: Optional[str] = None
