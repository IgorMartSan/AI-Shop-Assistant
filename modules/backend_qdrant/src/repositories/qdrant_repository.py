from __future__ import annotations

import logging
from typing import Any
import os

from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger(__name__)


class QdrantRepositoryError(RuntimeError):
    pass


class QdrantRepository:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_sec: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        resolved_base_url = base_url or os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
        self._base_url = resolved_base_url.rstrip("/")
        self._timeout = timeout_sec
        self._session = session or requests.Session()

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        with_payload: bool,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query_vector,
            "limit": limit,
            "with_payload": with_payload,
        }
        response = self._request(
            "POST",
            f"/collections/{collection_name}/points/query",
            json=payload,
        )
        result = response.get("result", [])
        if isinstance(result, dict):
            points = result.get("points", [])
        else:
            points = result
        if not isinstance(points, list):
            raise QdrantRepositoryError(
                "Qdrant returned an unexpected payload for search"
            )
        return points

    def list_collections(self) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/collections",
        )
        result = response.get("result", {})
        collections = result.get("collections", [])
        if not isinstance(collections, list):
            raise QdrantRepositoryError(
                "Qdrant returned an unexpected payload for collections"
            )
        return collections

    def create_points(
        self,
        collection_name: str,
        points: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {"points": points}
        response = self._request(
            "PUT",
            f"/collections/{collection_name}/points",
            json=payload,
        )
        return response

    def get_point(
        self,
        collection_name: str,
        point_id: str | int,
        with_payload: bool = True,
        with_vector: bool = False,
    ) -> Optional[dict[str, Any]]:
        params = {
            "with_payload": with_payload,
            "with_vector": with_vector,
        }
        response = self._request(
            "GET",
            f"/collections/{collection_name}/points/{point_id}",
            params=params,
        )
        return response.get("result")

    def update_point(
        self,
        collection_name: str,
        point_id: str | int,
        vector: Optional[list[float]] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        update_payload = {}
        if vector is not None:
            update_payload["vector"] = vector
        if payload is not None:
            update_payload["payload"] = payload

        response = self._request(
            "PATCH",
            f"/collections/{collection_name}/points/{point_id}",
            json=update_payload,
        )
        return response

    def delete_point(
        self,
        collection_name: str,
        point_id: str | int,
    ) -> dict[str, Any]:
        response = self._request(
            "DELETE",
            f"/collections/{collection_name}/points/{point_id}",
        )
        return response

    def delete_points(
        self,
        collection_name: str,
        point_ids: list[str | int],
    ) -> dict[str, Any]:
        payload = {"points": point_ids}
        response = self._request(
            "POST",
            f"/collections/{collection_name}/points/delete",
            json=payload,
        )
        return response

    def list_points(
        self,
        collection_name: str,
        limit: int = 100,
        offset: Optional[int] = None,
        with_payload: bool = True,
        with_vector: bool = False,
    ) -> dict[str, Any]:
        params = {
            "limit": limit,
            "with_payload": with_payload,
            "with_vector": with_vector,
        }
        if offset is not None:
            params["offset"] = offset

        response = self._request(
            "GET",
            f"/collections/{collection_name}/points",
            params=params,
        )
        result = response.get("result", {})
        if not isinstance(result, dict):
            raise QdrantRepositoryError(
                "Qdrant returned an unexpected payload for point listing"
            )

        points = result.get("points", [])
        next_page_offset = result.get("next_page_offset")
        if not isinstance(points, list):
            raise QdrantRepositoryError(
                "Qdrant returned an unexpected list of points"
            )

        return {
            "result": points,
            "next_page_offset": next_page_offset,
        }

    def list_all_points(
        self,
        collection_name: str,
        batch_limit: int = 100,
        with_payload: bool = True,
        with_vector: bool = False,
    ) -> dict[str, Any]:
        all_points: list[dict[str, Any]] = []
        next_offset: Optional[int] = None

        while True:
            page = self.list_points(
                collection_name=collection_name,
                limit=batch_limit,
                offset=next_offset,
                with_payload=with_payload,
                with_vector=with_vector,
            )
            points = page.get("result", [])
            if not isinstance(points, list):
                raise QdrantRepositoryError(
                    "Qdrant returned an unexpected payload while iterating points"
                )

            all_points.extend(points)
            next_offset = page.get("next_page_offset")
            if next_offset is None:
                break

        return {
            "result": all_points,
            "total": len(all_points),
        }

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
            logger.exception("Qdrant request failed for %s", url)
            raise QdrantRepositoryError(f"Request failed for {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip()
            logger.error(
                "Qdrant returned error status | url=%s | status_code=%s | detail=%s",
                url,
                response.status_code,
                detail,
            )
            raise QdrantRepositoryError(
                f"Qdrant returned {response.status_code} for {url}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            logger.exception("Qdrant returned invalid JSON for %s", url)
            raise QdrantRepositoryError(
                f"Qdrant returned invalid JSON for {url}"
            ) from exc
