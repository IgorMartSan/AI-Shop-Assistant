
import time

from infra.embedding_client import EmbeddingClient, EmbeddingClientError
from infra.environment import Environment

TEST_TEXT = """
Deep learning is a field of machine learning that uses neural networks with many layers
to learn patterns from text, images, audio, and other types of data.
"""


def main():
    env = Environment()
    client = EmbeddingClient(base_url=env.EMBEDDING_API_BASE_URL)

    try:
        started_at = time.perf_counter()
        embedding = client.embed(TEST_TEXT.strip())
        elapsed_seconds = time.perf_counter() - started_at
    except EmbeddingClientError as exc:
        print(f"Falha ao gerar embedding: {exc}")
        raise

    print(f"Texto: {TEST_TEXT.strip()}")
    print(f"Dimensao do embedding: {len(embedding[0]) if embedding and isinstance(embedding[0], list) else len(embedding)}")
    print(embedding)
    print(f"Tempo de execucao: {elapsed_seconds:.4f} segundos")


if __name__ == "__main__":
    main()
