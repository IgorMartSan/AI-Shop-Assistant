import os
from typing import Optional

import redis


class RedisConnection:
    """
    Classe responsável por gerenciar a conexão com o Redis.
    Implementa um padrão Singleton simples.
    """

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_DECODE_RESPONSES: bool = True

    _client: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Retorna uma instância única do cliente Redis.
        """
        if cls._client is None:
            cls._client = redis.Redis(
                host=cls.REDIS_HOST,
                port=cls.REDIS_PORT,
                db=cls.REDIS_DB,
                decode_responses=cls.REDIS_DECODE_RESPONSES,
            )

        return cls._client