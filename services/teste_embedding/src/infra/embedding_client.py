from __future__ import annotations

from typing import Any

import requests


class EmbeddingClientError(RuntimeError):
    pass


class EmbeddingClient:
    def __init__(
        self,
        base_url: str,
        timeout_sec: float = 120.0,
        session: requests.Session | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required for EmbeddingClient")

        self._base_url = base_url.rstrip("/")
        self._timeout = float(timeout_sec)
        self._session = session or requests.Session()




    def embed(self, inputs: str | list[str]) -> list[Any]:
        payload = {"inputs": inputs}
        return self._request("POST", "/embed", json=payload)



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
            raise EmbeddingClientError(f"Request failed for {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip()
            raise EmbeddingClientError(
                f"Embedding API returned {response.status_code} for {url}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise EmbeddingClientError(
                f"Embedding API returned invalid JSON for {url}"
            ) from exc
