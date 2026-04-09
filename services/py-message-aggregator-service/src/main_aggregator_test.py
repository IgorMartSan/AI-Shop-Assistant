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
            print(f"Enviando para {user_id}: Oi")
            repo.add_message(user_id, "Oi")
            sleep(15)
            print(f"Enviando para {user_id}: Vocês têm notebook?")
            repo.add_message(user_id, "Vocês têm notebook?")
            sleep(15)
            print(f"Enviando para {user_id}: Qual o valor?")
            repo.add_message(user_id, "Qual o valor?")
            
            cont += 1
            user_id = cont
            print(f"Adicionando mensagens para user_id={user_id}")
            # simulando mensagens
            print(f"Enviando para {user_id}: Bom dia")
            repo.add_message(user_id, "Bom dia")
            sleep(15)
            print(f"Enviando para {user_id}: Tem notebook disponível?")
            repo.add_message(user_id, "Tem notebook disponível?")
            sleep(15)
            print(f"Enviando para {user_id}: Qual a faixa de preço?")
            repo.add_message(user_id, "Qual a faixa de preço?")
            cont += 1
            sleep(60)


            


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Ocorreu um erro:", str(e))
