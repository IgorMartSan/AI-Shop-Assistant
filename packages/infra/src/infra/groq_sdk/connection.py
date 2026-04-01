import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)


class GroqConnection:
    """
    Gerencia a conexão com a API da Groq.

    Responsável por:
    - Criar cliente único
    - Validar configuração mínima
    - Expor o cliente Groq

    NÃO deve conter lógica de negócio.

    Exemplo de uso:

    ```python
    from infra.groq_sdk import GroqConnection

    client = GroqConnection().get_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Voce e um assistente objetivo.",
            },
            {
                "role": "user",
                "content": "Explique a importancia de modelos rapidos.",
            },
        ],
        temperature=0.7,
        max_tokens=300,
    )

    print(response.choices[0].message.content)
    ```

    Argumentos comuns ao enviar mensagens:
    - `model`: nome do modelo que sera usado.
    - `messages`: lista de mensagens no formato chat com `role` e `content`.
    - `temperature`: controla variacao da resposta.
    - `max_tokens`: limita o tamanho da saida.
    - `top_p`: alternativa para controlar diversidade.
    - `stream`: retorna a resposta em partes quando `True`.
    - `stop`: define sequencias para encerrar a geracao.

    Outros argumentos podem existir conforme a versao do SDK e o endpoint usado.
    A `GroqConnection` apenas entrega o cliente autenticado; a chamada e os
    parametros da completacao ficam na camada de servico ou de caso de uso.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        self._client: Groq | None = None

        self._connect()

    def _connect(self) -> None:
        """Inicializa o cliente da Groq."""
        try:
            if not self.api_key:
                raise RuntimeError("GROQ_API_KEY não configurada")

            self._client = Groq(api_key=self.api_key)
            logger.info("Cliente Groq inicializado com sucesso")

        except Exception:
            logger.exception("Erro ao inicializar cliente Groq")
            raise

    def get_client(self) -> Groq:
        """Retorna o cliente Groq ativo."""
        if not self._client:
            raise RuntimeError("Cliente Groq não está inicializado")
        return self._client
