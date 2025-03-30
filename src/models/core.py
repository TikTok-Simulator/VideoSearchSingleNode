import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs


load_dotenv()
_TWELVE_LABS_API_KEY = os.getenv("TWELVE_LABS_API_KEY")
twelvelabs_client = TwelveLabs(api_key=_TWELVE_LABS_API_KEY)

model_name = "Marengo-retrieval-2.7"
