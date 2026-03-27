import os
import logging
from redis import Redis
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class RedisConnection:
    """
    Gerencia a conexão com o Redis.

    Responsável por:
    - Criar conexão única
    - Reutilizar cliente Redis
    - Validar conexão

    Variáveis esperadas no .env:
        REDIS_HOST
        REDIS_PORT
        REDIS_DB
    """

    def __init__(self):
        load_dotenv()

        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))

        self._client: Redis | None = None

        self._connect()

    def _connect(self):
        """Inicializa a conexão com o Redis."""
        try:
            self._client = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,  # retorna string em vez de bytes
            )

            # Teste de conexão
            self._client.ping()

            logger.info("✅ Conectado ao Redis com sucesso")

        except Exception as e:
            logger.exception("❌ Erro ao conectar no Redis")
            raise e

    def get_client(self) -> Redis:
        """Retorna o cliente Redis ativo."""
        if not self._client:
            raise RuntimeError("Redis não está conectado")
        return self._client