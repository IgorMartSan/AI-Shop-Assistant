from __future__ import annotations

from typing import Any

import requests


class QdrantClientError(RuntimeError):
    pass


class QdrantClient:
    def __init__(
        self,
        base_url: str,
        timeout_sec: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required for QdrantClient")

        self._base_url = base_url.rstrip("/")
        self._timeout = float(timeout_sec)
        self._session = session or requests.Session()

    def recreate_collection(self, collection_name: str, vector_size: int) -> dict[str, Any]:
        payload = {
            "vectors": {
                "size": vector_size,
                "distance": "Cosine",
            }
        }
        return self._request("PUT", f"/collections/{collection_name}", json=payload)

    def upsert_points(self, collection_name: str, points: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"points": points}
        return self._request("PUT", f"/collections/{collection_name}/points", json=payload)

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query_vector,
            "limit": limit,
            "with_payload": True,
        }
        response = self._request("POST", f"/collections/{collection_name}/points/query", json=payload)
        result = response.get("result", [])
        if isinstance(result, dict):
            points = result.get("points", [])
        else:
            points = result
        if not isinstance(points, list):
            raise QdrantClientError("Qdrant returned an unexpected payload for search")
        return points

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
            raise QdrantClientError(f"Request failed for {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip()
            raise QdrantClientError(
                f"Qdrant returned {response.status_code} for {url}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise QdrantClientError(f"Qdrant returned invalid JSON for {url}") from exc
