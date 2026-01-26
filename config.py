import os
from pathlib import Path
from dotenv import load_dotenv

# loading .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# setting env variable
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
TOKEN_GET_URL = os.getenv("TOKEN_GET_URL")
STREAM_MANAGE_URL = os.getenv("STREAM_MANAGE_URL")
STREAM_LIST_URL = os.getenv("STREAM_LIST_URL")
STREAM_ADDRESS_URL = os.getenv("STREAM_ADDRESS_URL")