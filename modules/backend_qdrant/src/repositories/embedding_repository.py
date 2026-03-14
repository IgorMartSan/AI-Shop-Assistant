from __future__ import annotations

from typing import Any
import os

from dotenv import load_dotenv
import requests
from schemas.qdrant_schemas import EmbeddingRequest

load_dotenv()


class EmbeddingRepositoryError(RuntimeError):
    pass


class EmbeddingRepository:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_sec: float = 120.0,
        session: requests.Session | None = None,
    ) -> None:
        resolved_base_url = base_url or os.getenv(
            "EMBEDDING_API_BASE_URL", "http://127.0.0.1:8080"
        )
        self._base_url = resolved_base_url.rstrip("/")
        self._timeout = float(timeout_sec)
        self._session = session or requests.Session()

    def embed(self, request_data: EmbeddingRequest) -> list[Any]:
        response = self._request(
            "POST",
            "/embed",
            json=request_data.model_dump(),
        )
        if not isinstance(response, list):
            raise EmbeddingRepositoryError(
                "Embedding API returned an unexpected payload"
            )
        return response

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}{path}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
                **kwargs,
            )
        except requests.RequestException as exc:
            raise EmbeddingRepositoryError(f"Request failed for {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip()
            raise EmbeddingRepositoryError(
                f"Embedding API returned {response.status_code} for {url}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise EmbeddingRepositoryError(
                f"Embedding API returned invalid JSON for {url}"
            ) from exc
