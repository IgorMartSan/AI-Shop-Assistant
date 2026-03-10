import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "db": os.getenv("REDIS_DB"),
    "password": os.getenv("REDIS_PASSWORD")
}

class RedisClient:
    def __init__(self):
        self.client = None

    def connect(self):
        self.client = redis.Redis(
            host=REDIS_URL["host"],
            port=REDIS_URL["port"],
            db=REDIS_URL["db"],
            password=REDIS_URL["password"]
        )
        return self.client

    def get_client(self):
        if self.client is None:
            self.connect()
        return self.client

redis_client = RedisClient()

def get_redis():
    redis = redis_client.get_client()
    try:
        yield redis
    finally:
        pass  