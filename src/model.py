from .models.video_embedding import VideoEmbeddingModel
from .models.text_embedding import TextEmbeddingModel
from .schemas.input import TaskInput
from .schemas.output import TaskOutput


class MultimodalEmbeddingModel:
    def __init__(self):
        self.video_embedding_model = VideoEmbeddingModel()
        self.text_embedding_model = TextEmbeddingModel()

    def generate_embedding(self, input: TaskInput) -> TaskOutput:
        try:
            video = input.video

            if input.video_type == "url":
                video_embeddings, _ = self.video_embedding_model.generate_embedding_url(
                    video
                )
            elif input.video_type == "file":
                video_embeddings, _ = (
                    self.video_embedding_model.generate_embedding_file(video)
                )
            else:
                raise ValueError('Invalid video type. Should be "url" or "file".')

            video_embeddings_extended = [
                {
                    "video": video,
                    **dict_,
                }
                for _, dict_ in enumerate(video_embeddings)
            ]

            text_embeddings_extended = None

            if input.text is not None:
                text = input.text
                text_embeddings = self.text_embedding_model.generate_embedding(text)
                text_embeddings_extended = {
                    "text": text,
                    "embeddings_float": text_embeddings,
                }

            output_data = {
                "video_embeddings": video_embeddings_extended,
                "text_embedding": text_embeddings_extended,
            }

            return TaskOutput(**output_data)
        except Exception as e:
            raise e
