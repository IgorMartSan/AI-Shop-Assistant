import os
from dotenv import load_dotenv
from infra.redis.connection import RedisConnection
from infra.redis.repository import ChatBufferRepository

from time import sleep

load_dotenv()

def main() -> None:
    redis_conn = RedisConnection(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
    )
    repo = ChatBufferRepository(redis_conn)
    print("Aguardando...")
    cont = 0
    while True:
            user_id = cont
            print(f"Adicionando mensagens para user_id={user_id}")
            # simulando mensagens
            repo.add_message(user_id, "Oi")
            sleep(1)
            repo.add_message(user_id, "Quero pagar um boleto")
            sleep(1)
            repo.add_message(user_id, "vence hoje?")
            sleep(70)
            cont += 1


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Ocorreu um erro:", str(e))
