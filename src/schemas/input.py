from typing import Optional

from pydantic import BaseModel, Field, model_validator
from ..utils.validate_video import is_valid_video_url, is_valid_video_file


class TaskInput(BaseModel):
    video: str
    video_type: str = Field(default=None)  # Public field, initialized as None
    text: str

    @model_validator(mode="after")
    def set_video_type(self) -> "TaskInput":
        """
        Set 'video_type' based on whether 'video' is a URL or file after validation.
        """
        if is_valid_video_url(self.video):
            self.video_type = "url"
        elif is_valid_video_file(self.video):
            self.video_type = "file"
        return self
