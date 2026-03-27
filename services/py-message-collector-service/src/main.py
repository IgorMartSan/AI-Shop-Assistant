import logging
import os
import time

from dotenv import load_dotenv
from config.logger import setup_logger
from infra.redis import ChatBufferRepository, RedisConnection

load_dotenv()

setup_logger(
    container_name="py-message-collector-service",
    log_dir=os.getenv("LOG_DIR", os.path.join(os.getcwd(), "system_log")),
    show_log=True,
    error_mode="full",
)

logger = logging.getLogger(__name__)


def main() -> None:
        
        redis_conn = RedisConnection(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        )

        repo = ChatBufferRepository(redis_conn)

        while True:
            items = repo.collect_ready(
                idle_seconds=10,
                batch_size=10,
                lock_ttl_seconds=240,
            )

            print(f"Coletados {len(items)} itens prontos para processamento")

            for item in items:
                user_id = item["user_id"]
                messages = item["messages"]
                lock_token = item["lock_token"]

                try:
                    print(f"Processando user_id={user_id}: {messages}")




                    # seu processamento real aqui
                    # ex: LLM, banco, webhook, etc.





                    success = repo.ack_delete(user_id, lock_token)

                    if not success:
                        logger.warning(
                            "Não foi possível confirmar a deleção do user_id=%s",
                            user_id,
                        )

                except Exception:
                    logger.exception("Erro no processamento do user_id=%s", user_id)
                    repo.release_lock(user_id, lock_token)

            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Erro fatal na aplicação")
