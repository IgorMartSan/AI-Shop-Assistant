import time
from typing import Optional

import redis

from common.redis.connection import RedisConnection


class RedisRepository:
    """
    Repositório responsável por armazenar mensagens temporárias no Redis.

    Cada usuário possui:
    - uma lista de mensagens
    - um hash com metadados, como o timestamp da última mensagem
    - um índice global de usuários pendentes para processamento
    """

    PENDING_USERS_KEY: str = "pending_users"

    def __init__(self, client: Optional[redis.Redis] = None) -> None:
        """
        Inicializa o repositório com um cliente Redis.

        Args:
            client: Cliente Redis opcional. Se não for informado,
                    utiliza RedisConnection.get_client().
        """
        self.client: redis.Redis = client or RedisConnection.get_client()

    # =========================================================================
    # KEYS
    # =========================================================================

    def _messages_key(self, user_id: str) -> str:
        """
        Retorna a chave da lista de mensagens do usuário.
        """
        return f"user:{user_id}:messages"

    def _meta_key(self, user_id: str) -> str:
        """
        Retorna a chave de metadados do usuário.
        """
        return f"user:{user_id}:meta"

    def _lock_key(self, user_id: str) -> str:
        """
        Retorna a chave de lock do usuário.
        """
        return f"user:{user_id}:lock"

    # =========================================================================
    # MENSAGENS
    # =========================================================================

    def add_message(
        self,
        user_id: str,
        message: str,
        timestamp: Optional[int] = None,
    ) -> int:
        """
        Adiciona uma mensagem ao buffer do usuário.

        Se o timestamp não for informado, utiliza o timestamp atual.
        Também atualiza o horário da última mensagem e o índice global
        de usuários pendentes.

        Args:
            user_id: Identificador do usuário.
            message: Texto da mensagem.
            timestamp: Timestamp opcional em segundos.

        Returns:
            O timestamp utilizado na operação.
        """
        final_timestamp = timestamp or int(time.time())

        self.client.rpush(self._messages_key(user_id), message)

        self.client.hset(
            self._meta_key(user_id),
            mapping={
                "last_message_at": final_timestamp,
            },
        )

        self.client.zadd(
            self.PENDING_USERS_KEY,
            {user_id: final_timestamp},
        )

        return final_timestamp

    def get_messages(self, user_id: str) -> list[str]:
        """
        Retorna todas as mensagens armazenadas no buffer do usuário.

        Args:
            user_id: Identificador do usuário.

        Returns:
            Lista de mensagens.
        """
        return self.client.lrange(self._messages_key(user_id), 0, -1)

    def get_last_message_at(self, user_id: str) -> Optional[int]:
        """
        Retorna o timestamp da última mensagem do usuário.

        Args:
            user_id: Identificador do usuário.

        Returns:
            Timestamp da última mensagem ou None se não existir.
        """
        value = self.client.hget(self._meta_key(user_id), "last_message_at")
        return int(value) if value is not None else None

    def get_full_text(self, user_id: str, separator: str = " ") -> str:
        """
        Retorna todas as mensagens do usuário concatenadas em uma única string.

        Args:
            user_id: Identificador do usuário.
            separator: Separador usado entre as mensagens.

        Returns:
            Texto concatenado.
        """
        messages = self.get_messages(user_id)
        return separator.join(messages).strip()

    def clear_user_messages(self, user_id: str) -> None:
        """
        Remove do Redis os dados temporários do usuário.

        Args:
            user_id: Identificador do usuário.
        """
        self.client.delete(self._messages_key(user_id))
        self.client.delete(self._meta_key(user_id))
        self.client.zrem(self.PENDING_USERS_KEY, user_id)

    # =========================================================================
    # PENDÊNCIAS
    # =========================================================================

    def get_pending_users(self, limit_timestamp: int) -> list[str]:
        """
        Retorna usuários cuja última mensagem foi recebida até o timestamp informado.

        Isso permite buscar usuários que já ficaram tempo suficiente
        sem mandar nova mensagem.

        Args:
            limit_timestamp: Timestamp limite.

        Returns:
            Lista de user_ids.
        """
        return self.client.zrangebyscore(
            self.PENDING_USERS_KEY,
            0,
            limit_timestamp,
        )

    def remove_pending_user(self, user_id: str) -> None:
        """
        Remove o usuário do índice global de pendências.

        Args:
            user_id: Identificador do usuário.
        """
        self.client.zrem(self.PENDING_USERS_KEY, user_id)

    # =========================================================================
    # LOCK
    # =========================================================================

    def acquire_lock(self, user_id: str, ttl_seconds: int = 30) -> bool:
        """
        Tenta adquirir um lock para o usuário.

        Args:
            user_id: Identificador do usuário.
            ttl_seconds: Tempo de expiração do lock.

        Returns:
            True se conseguiu adquirir o lock, False caso contrário.
        """
        return bool(
            self.client.set(
                self._lock_key(user_id),
                "1",
                nx=True,
                ex=ttl_seconds,
            )
        )

    def release_lock(self, user_id: str) -> None:
        """
        Libera o lock do usuário.

        Args:
            user_id: Identificador do usuário.
        """
        self.client.delete(self._lock_key(user_id))