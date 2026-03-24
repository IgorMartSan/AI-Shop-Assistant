import redis
import atexit
import pickle
from prometheus_client import Summary, Counter
from typing import Optional, Tuple, Any

STREAM_WRITE_TIME = Summary('redis_queue_write_time_seconds', 'Time spent writing to the queue redis')
STREAM_READ_TIME = Summary('redis_queue_read_time_seconds', 'Time spent reading from the queue')
PUSH_COUNTER = Counter('redis_queue_write_total', 'Total number of Redis write operations performed')
READ_COUNTER = Counter('redis_queue_read_total', 'Total number of Redis read operations performed')


class RedisConnection:
    def __init__(self, host: str, port: int, db: str):
        """
        Initializes the connection to the Redis server.

        Loads Redis server settings from environment variables.
        
        Inicializa a conexão com o servidor Redis.

        Carrega as configurações do servidor Redis a partir de variáveis de ambiente.
        """
    
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db
        )


    def get_connection(self):
        """
        Returns the Redis client for operations.

        Returns:
            Redis: The Redis client for executing operations.
            
        Retorna o cliente Redis para operações.
        """
        return self.redis_client

    def __destroy_connection(self):
        """
        Ends the connection to the Redis server.

        Closes the connection to the Redis server when the instance is terminated.
        
        Finaliza a conexão com o servidor Redis.

        Fecha a conexão com o servidor Redis quando a instância é encerrada.
        """
        print("Connection terminated")
        self.redis_client.close()


    ###################################################################################
        
    @STREAM_WRITE_TIME.time()
    def add_to_stream(self, data: Any, stream_key:str,  max_len:int = 50):
            """
            Adiciona dados a um stream no Redis.
            Args:
                stream_name (str): Nome do stream onde os dados serão adicionados.
                data: Dados a serem adicionados como um dicionário, deve ser serializado com a biblioteca pickle.
                maxlen (int, optional): Tamanho máximo do stream. Default é None.
                approximate (bool, optional): Se True, remove entradas antigas para respeitar maxlen. Default é True.

            Returns:
                str: O ID da entrada adicionada.
            """
            
            serialized_data = pickle.dumps(data)
            
            entry_id = self.redis_client.xadd(
                stream_key,
                {"data_serialized": serialized_data},
                maxlen=max_len,
                approximate=True
            )

            # Increment the counter for each read operation
            PUSH_COUNTER.inc()
            return entry_id
    
    @STREAM_READ_TIME.time()
    def get_from_stream(self, stream_key: str, last_id: str = "0") -> Tuple[Optional[Any], str]:
        """
        Lê uma única entrada do stream no Redis.

        Retorno (contrato estável):
            - (data, new_last_id) quando houver mensagem
            - (None, last_id) quando o stream estiver vazio (timeout)
        """
        stream_messages = self.redis_client.xread(
            {stream_key: last_id},
            count=1,
            block=5000
        )

        if stream_messages:
            _stream_name, message_list = stream_messages[0]
            current_id, fields = message_list[0]

            data_serialized = fields.get(b"data_serialized")
            if data_serialized is None:
                return None, last_id  # mensagem inválida, não quebra o loop

            deserialized_data = pickle.loads(data_serialized)

            READ_COUNTER.inc()

            # current_id pode ser bytes
            new_last_id = current_id.decode() if isinstance(current_id, (bytes, bytearray)) else str(current_id)
            return deserialized_data, new_last_id

        # ✅ stream vazio -> mantém last_id anterior
        return None, last_id

    def get_stream_length(self, stream_name):
        """
        Returns the length of the stream.

        Args:
            stream_name (str): Name of the stream.

        Returns:
            int: Length of the stream.
            
        Retorna o comprimento do stream.

        Args:
            stream_name (str): Nome do stream.

        Returns:
            int: Comprimento do stream.
        """
        stream_length = self.redis_client.xlen(stream_name)
        return stream_length
    


    #######################################################################

    def insert_dict_to_redis(self, key, data):
        """
        Inserts a dictionary into Redis.

        Args:
            key (str): Key for the dictionary.
            data (dict): Dictionary to be inserted.
            
        Insere um dicionário no Redis.

        Args:
            key (str): Chave para o dicionário.
            data (dict): Dicionário a ser inserido.
        """
        serialized_data = pickle.dumps(data)
        self.redis_client.set(key, serialized_data)

    def get_dict_from_redis(self, key):
        """
        Retrieves a dictionary from Redis.

        Args:
            key (str): Key for the dictionary.

        Returns:
            dict: Dictionary retrieved from Redis.
            
        Recupera um dicionário do Redis.

        Args:
            key (str): Chave para o dicionário.

        Returns:
            dict: Dicionário recuperado do Redis.
        """
        
        serialized_data = self.redis_client.get(key)
        if serialized_data:
            deserialized_data = pickle.loads(serialized_data)
            return deserialized_data
        else:
            return None


    def insert_dict_to_redis(self, key, data):
        """
        Inserts a dictionary into Redis.

        Args:
            key (str): Key for the dictionary.
            data (dict): Dictionary to be inserted.
            
        Insere um dicionário no Redis.

        Args:
            key (str): Chave para o dicionário.
            data (dict): Dicionário a ser inserido.
        """
        serialized_data = pickle.dumps(data)
        self.redis_client.set(key, serialized_data)

    def get_dict_from_redis(self, key):
        """
        Retrieves a dictionary from Redis.

        Args:
            key (str): Key for the dictionary.

        Returns:
            dict: Dictionary retrieved from Redis.
            
        Recupera um dicionário do Redis.

        Args:
            key (str): Chave para o dicionário.

        Returns:
            dict: Dicionário recuperado do Redis.
        """
        serialized_data = self.redis_client.get(key)
        if serialized_data:
            deserialized_data = pickle.loads(serialized_data)
            return deserialized_data
        else:
            return None
        


    def set_object(self, key: str, obj: Any, ttl: Optional[int] = None) -> None:
        """
        Store a Python object in Redis serialized with pickle.

        Args:
            key: Redis key.
            obj: Python object to serialize.
            ttl: Optional expiration in seconds (None = no expiry).

        Raises:
            redis.RedisError: On write failure.

        Security:
            Only pickle data you trust (pickle can execute arbitrary code).
        """
        blob = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        if ttl is not None:
            self.redis_client.setex(key, ttl, blob)
        else:
            self.redis_client.set(key, blob)


    def get_object(self, key: str) -> Any | None:
        """
        Load a Python object from Redis previously stored via pickle.

        Args:
            key: Redis key.

        Returns:
            The deserialized object, or None if the key does not exist.

        Raises:
            redis.RedisError: On read failure.
            pickle.UnpicklingError: If data is not valid pickle.

        Security:
            Only unpickle data from trusted sources.
        """
        data = self.redis_client.get(key)
        if data is None:
            return None
        return pickle.loads(data)
