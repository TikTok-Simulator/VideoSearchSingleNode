from typing import List

from .core import model_name, twelvelabs_client


class TextEmbeddingModel:
    def __init__(self):
        self.twelvelabs_client = twelvelabs_client
        
    def generate_embedding(self, text: str) -> List[List[float]]:
        res = self.twelvelabs_client.embed.create(
            model_name=model_name,
            text=text
        )
        
        if res.text_embedding is not None and res.text_embedding.segments is not None:
            segments =  res.text_embedding.segments
            embeddings = [segment.embeddings_float for segment in segments]
            return embeddings[0]
        else:
            return None
