
import time

from infra.embedding_client import EmbeddingClient, EmbeddingClientError


EMBEDDING_API_BASE_URL = "http://127.0.0.1:8080"
INPUT_TEXT = "What is Deep Learning?"


def main():
    client = EmbeddingClient(base_url=EMBEDDING_API_BASE_URL)

    try:
        started_at = time.perf_counter()
        embeddings = client.embed(INPUT_TEXT)
        elapsed_seconds = time.perf_counter() - started_at
    except EmbeddingClientError as exc:
        print(f"Falha ao gerar embedding: {exc}")
        raise

    print(embeddings)
    print(f"Tempo de execucao: {elapsed_seconds:.4f} segundos")


if __name__ == "__main__":
    main()
