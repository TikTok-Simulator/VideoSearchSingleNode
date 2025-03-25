import os
from dotenv import load_dotenv


load_dotenv()


class VideoSearch:
    def __init__(self):
        self.api_key = os.getenv("TWELVE_LABS_API_KEY")
