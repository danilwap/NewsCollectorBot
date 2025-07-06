import os
from dotenv import load_dotenv

load_dotenv()


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
target_forum_id = int(os.getenv('TARGET_FORUM_ID'))