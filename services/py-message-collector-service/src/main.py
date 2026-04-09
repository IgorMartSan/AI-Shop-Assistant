import logging
import os
import time
from urllib.parse import quote_plus

from dotenv import load_dotenv
from config.logger import setup_logger
from infra.redis import ChatBufferRepository, RedisConnection
from infra.mongo.connection import MongoConnection
from infra.mongo.longtermrepository import LongTermRepository
from infra.mongo.shorttermrepository import ShortTermRepository
from state_machine.machine import build_conversation_graph
from state_machine.services import build_graph_dependencies


load_dotenv()

setup_logger(
    container_name="py-message-collector-service",
    log_dir=os.getenv("LOG_DIR", os.path.join(os.getcwd(), "system_log")),
    show_log=True,
    error_mode="full",
)

logger = logging.getLogger(__name__)


def build_mongo_uri() -> str:
    direct_uri = os.getenv("MONGO_URI")
    if direct_uri:
        return direct_uri

    host = os.getenv("MONGO_HOST", "localhost")
    port = int(os.getenv("MONGO_PORT", 27017))
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

    if username and password:
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        return (
            f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}/"
            f"?authSource={quote_plus(auth_source)}"
        )

    return f"mongodb://{host}:{port}"


def main() -> None:
    platform = os.getenv("MESSAGE_PLATFORM", "redis_buffer")
    long_term_threshold = int(os.getenv("LONG_TERM_UPDATE_EVERY", 10))

    redis_conn = RedisConnection(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
    )

    redis_repo_chatbuffer = ChatBufferRepository(redis_conn)

    mongo_conn = MongoConnection(
        uri=build_mongo_uri(),
        database_name=os.getenv("MONGO_DB", "chat_db"),
    )

    mongo_repo_longterm = LongTermRepository(mongo_conn)
    mongo_repo_shortterm = ShortTermRepository(mongo_conn)

    graph = build_conversation_graph(
        build_graph_dependencies(
            short_term_repository=mongo_repo_shortterm,
            long_term_repository=mongo_repo_longterm,
            long_term_threshold=long_term_threshold,
        )
    )

    while True:
        items = redis_repo_chatbuffer.collect_ready(
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

                result = graph.invoke(
                    {
                        "platform": platform,
                        "user_id": user_id,
                        "messages": messages,
                    }
                )

                success = redis_repo_chatbuffer.ack_delete(user_id, lock_token)

                if not success:
                    logger.warning(
                        "Não foi possível confirmar a deleção do user_id=%s",
                        user_id,
                    )
                else:
                    logger.info(
                        "Pipeline processada para user_id=%s com ação=%s",
                        user_id,
                        result.get("action"),
                    )
                    logger.info(
                        "Resposta final para user_id=%s: %s",
                        user_id,
                        result.get("final_response", ""),
                    )

            except Exception:
                logger.exception("Erro no processamento do user_id=%s", user_id)
                redis_repo_chatbuffer.release_lock(user_id, lock_token)

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Erro fatal na aplicação")
