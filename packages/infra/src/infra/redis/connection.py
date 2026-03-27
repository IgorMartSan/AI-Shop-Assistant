import logging

from redis import Redis

logger = logging.getLogger(__name__)


class RedisConnection:
    """
    Gerencia a conexão com o Redis.

    Responsável por:
    - Criar conexão única
    - Reutilizar cliente Redis
    - Validar conexão

    Parâmetros esperados:
        host
        port
        db
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
    ):
        self.host = host
        self.port = port
        self.db = db

        self._client: Redis | None = None

        self._connect()

    def _connect(self):
        """Inicializa a conexão com o Redis."""
        try:
            self._client = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
            )

            self._client.ping()
            logger.info("Conectado ao Redis com sucesso")

        except Exception as e:
            logger.exception("Erro ao conectar no Redis")
            raise e

    def get_client(self) -> Redis:
        """Retorna o cliente Redis ativo."""
        if not self._client:
            raise RuntimeError("Redis não está conectado")
        return self._client
