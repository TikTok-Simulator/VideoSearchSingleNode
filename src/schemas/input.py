from typing import Optional

from pydantic import BaseModel


class TaskInput(BaseModel):
    video_url: str
    text: Optional[str] = None
    