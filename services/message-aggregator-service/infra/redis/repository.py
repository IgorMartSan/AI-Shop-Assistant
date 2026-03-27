import time
import uuid
import logging
from typing import List, Dict, Any
from redis import Redis

logger = logging.getLogger(__name__)


class ChatBufferRepository:
    """
    Gerencia buffer de mensagens por usuário com lock de processamento.

    Estrutura no Redis:
    - Lista:
        chat:buffer:{user_id}

    - Sorted Set:
        chat:ready_index

    - Lock:
        chat:processing:{user_id}
    """

    def __init__(self, redis_connection):
        self.redis: Redis = redis_connection.get_client()

        self.buffer_prefix = "chat:buffer"
        self.index_key = "chat:ready_index"
        self.processing_prefix = "chat:processing"

    def _buffer_key(self, user_id: str) -> str:
        return f"{self.buffer_prefix}:{user_id}"

    def _lock_key(self, user_id: str) -> str:
        return f"{self.processing_prefix}:{user_id}"

    # ================================
    # ADD MESSAGE
    # ================================
    def add_message(self, user_id: str, message: str) -> None:
        try:
            now = time.time()

            pipe = self.redis.pipeline()
            pipe.rpush(self._buffer_key(user_id), message)
            pipe.zadd(self.index_key, {str(user_id): now})
            pipe.execute()

        except Exception:
            logger.exception("Erro ao adicionar mensagem")
            raise

    # ================================
    # COLLECT SEM DELETE
    # ================================
    def collect_ready(
        self,
        idle_seconds: int = 60,
        batch_size: int | None = None,
        lock_ttl_seconds: int = 240,
    ) -> List[Dict[str, Any]]:
        """
        Busca usuários prontos, tenta adquirir lock e retorna mensagens
        sem deletar.

        Returns:
            [
                {
                    "user_id": str,
                    "messages": List[str],
                    "full_text": str,
                    "lock_token": str,
                }
            ]
        """
        try:
            cutoff = time.time() - idle_seconds

            users = self.redis.zrangebyscore(
                self.index_key,
                min=0,
                max=cutoff,
            )

            if batch_size:
                users = users[:batch_size]

            results: List[Dict[str, Any]] = []

            for raw_user_id in users:
                user_id = (
                    raw_user_id.decode("utf-8")
                    if isinstance(raw_user_id, bytes)
                    else str(raw_user_id)
                )

                lock_token = str(uuid.uuid4())

                acquired = self.redis.set(
                    self._lock_key(user_id),
                    lock_token,
                    nx=True,
                    ex=lock_ttl_seconds,
                )

                if not acquired:
                    continue

                try:
                    messages = self.redis.lrange(self._buffer_key(user_id), 0, -1)

                    messages = [
                        msg.decode("utf-8") if isinstance(msg, bytes) else str(msg)
                        for msg in messages
                    ]

                    if not messages:
                        self.release_lock(user_id, lock_token)
                        self.redis.zrem(self.index_key, user_id)
                        continue

                    results.append(
                        {
                            "user_id": user_id,
                            "messages": messages,
                            "full_text": "\n".join(messages),
                            "lock_token": lock_token,
                        }
                    )

                except Exception:
                    logger.exception(
                        "Erro ao coletar mensagens do user_id=%s",
                        user_id,
                    )
                    self.release_lock(user_id, lock_token)

            return results

        except Exception:
            logger.exception("Erro ao coletar mensagens prontas")
            raise

    # ================================
    # DELETE FINAL COM TOKEN
    # ================================
    def ack_delete(self, user_id: str, lock_token: str) -> bool:
        """
        Deleta buffer + índice + lock apenas se o token do lock for válido.

        Returns:
            True se deletou com sucesso, False caso contrário.
        """
        try:
            script = """
            local lock_key = KEYS[1]
            local buffer_key = KEYS[2]
            local index_key = KEYS[3]

            local expected_token = ARGV[1]
            local user_id = ARGV[2]

            local current_token = redis.call("GET", lock_key)

            if not current_token then
                return 0
            end

            if current_token ~= expected_token then
                return 0
            end

            redis.call("DEL", buffer_key)
            redis.call("ZREM", index_key, user_id)
            redis.call("DEL", lock_key)

            return 1
            """

            result = self.redis.eval(
                script,
                3,
                self._lock_key(user_id),
                self._buffer_key(user_id),
                self.index_key,
                lock_token,
                str(user_id),
            )

            return result == 1

        except Exception:
            logger.exception("Erro ao confirmar deleção do user_id=%s", user_id)
            raise

    # ================================
    # LIBERA LOCK EM CASO DE ERRO
    # ================================
    def release_lock(self, user_id: str, lock_token: str) -> bool:
        """
        Libera o lock somente se ele ainda pertencer a este processamento.
        """
        try:
            script = """
            local lock_key = KEYS[1]
            local expected_token = ARGV[1]

            local current_token = redis.call("GET", lock_key)

            if not current_token then
                return 0
            end

            if current_token ~= expected_token then
                return 0
            end

            redis.call("DEL", lock_key)
            return 1
            """

            result = self.redis.eval(
                script,
                1,
                self._lock_key(user_id),
                lock_token,
            )

            return result == 1

        except Exception:
            logger.exception("Erro ao liberar lock do user_id=%s", user_id)
            raise

    # ================================
    # RENOVA LOCK
    # ================================
    def renew_lock(
        self,
        user_id: str,
        lock_token: str,
        lock_ttl_seconds: int = 240,
    ) -> bool:
        """
        Renova o TTL do lock se ele ainda for válido.
        """
        try:
            script = """
            local lock_key = KEYS[1]
            local expected_token = ARGV[1]
            local ttl = tonumber(ARGV[2])

            local current_token = redis.call("GET", lock_key)

            if not current_token then
                return 0
            end

            if current_token ~= expected_token then
                return 0
            end

            redis.call("EXPIRE", lock_key, ttl)
            return 1
            """

            result = self.redis.eval(
                script,
                1,
                self._lock_key(user_id),
                lock_token,
                lock_ttl_seconds,
            )

            return result == 1

        except Exception:
            logger.exception("Erro ao renovar lock do user_id=%s", user_id)
            raise