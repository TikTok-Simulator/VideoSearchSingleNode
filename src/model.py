import logging

from .models.video_embedding import VideoEmbeddingModel
from .models.text_embedding import TextEmbeddingModel
from .schemas.input import TaskInput
from .schemas.output import TaskOutput, RetrievalOutput
from .milvus import MilvusDatabase


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

    def query_embedding_node(
        self,
        input: TaskInput,
        milvus: MilvusDatabase,
        video_collection_name: str,
        limit: int = 10,
    ) -> TaskOutput:
        video_embeddings = milvus.query_by_metadata(
            collection_name=video_collection_name,
            filter_metadata=f'video=="{input.video}"',
            output_fields=None,
            limit=limit,
        )
        video_embeddings_extended = [
            {
                **dict_,
            }
            for _, dict_ in enumerate(video_embeddings)
        ]
        output_data = {
            "video_embeddings": video_embeddings_extended,
            "text_embedding": None,
        }

        return TaskOutput(**output_data)

    def retrieve_similarity_from_milvus(
        self,
        input: TaskInput,
        milvus: MilvusDatabase,
        video_collection_name: str,
        text_collection_name: str,
        limit: int = 10,
    ) -> RetrievalOutput:
        logging.info(f"Retrieving similarity from milvus for the video {input.video}")
        print(f"Retrieving similarity from milvus for the video {input.video}")

        # Replace generate input video into filter due to
        # the video already exist in our system and had been embedded
        def _query():
            task_output = self.query_embedding_node(
                input, milvus, video_collection_name, limit=10
            )

            video_embeddings_float = [
                embedding.embeddings_float
                for embedding in task_output.video_embeddings
                if embedding.embedding_scope == "video"
                and embedding.video == input.video
            ]
            return task_output, video_embeddings_float

        def _generate():
            task_output = self.generate_embedding(input=input)

            video_embeddings_float = [
                embedding.embeddings_float
                for embedding in task_output.video_embeddings
                if embedding.embedding_scope == "video"
                and embedding.video == input.video
            ]
            return task_output, video_embeddings_float

        task_output, video_embeddings_float = _query()

        # TODO: used for user's uploaded videos (in future)
        if not video_embeddings_float:
            logging.warning("Query not found => Generating the embedding")
            task_output, video_embeddings_float = _generate()

        if not video_embeddings_float:
            raise ValueError("Error when generating video embedding")

        results = {}

        video_results = milvus.retrieve_similarity(
            video_collection_name,
            video_embeddings_float,
            limit,
            ["video", "embedding_scope"],
        )
        videos = [
            video_result["entity"]["video"]
            for video_result in video_results
            if video_result["entity"]["embedding_scope"] == "video"
        ]
        results["videos"] = videos

        if task_output.text_embedding:
            text_embedding_float = task_output.text_embedding.embeddings_float
            text_results = milvus.retrieve_similarity(
                text_collection_name, [text_embedding_float], limit, ["text"]
            )
            text_list = [text_result["entity"]["text"] for text_result in text_results]
            results["text_list"] = text_list

        logging.info(f"Retrieved list of videos: {results['videos']}")
        print(f"Retrieved list of videos: {results['videos']}")
        return RetrievalOutput(**results)
