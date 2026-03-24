from __future__ import annotations

from typing import Any, Optional

import requests


class SisatApiError(RuntimeError):
    pass


class SisatApiClient:
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout_sec: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required for SisatApiClient")
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._username = username
        self._password = password
        self._timeout = float(timeout_sec)
        self._session = session or requests.Session()

        if not self._token and self._username and self._password:
            self._login()

    def _login(self) -> None:
        if not self._username or not self._password:
            raise SisatApiError("Missing username/password for Sisat API login")

        url = f"{self.base_url}/auth/token"
        resp = self._session.post(
            url,
            data={"username": self._username, "password": self._password},
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise SisatApiError(
                f"Auth failed ({resp.status_code}): {resp.text}"
            )
        data = resp.json() or {}
        token = data.get("access_token")
        if not token:
            raise SisatApiError("Auth succeeded but no access_token in response")
        self._token = token

    def _headers(self, extra: Optional[dict[str, str]] = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        headers = self._headers(kwargs.pop("headers", None))
        try:
            resp = self._session.request(
                method,
                url,
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            )
        except requests.RequestException as e:
            # If there's a transport error and we can re-auth, try once.
            if self._username and self._password:
                self._login()
                headers = self._headers(kwargs.pop("headers", None))
                resp = self._session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self._timeout,
                    **kwargs,
                )
            else:
                raise SisatApiError(f"Request failed: {e}") from e

        if resp.status_code in {401, 403} and self._username and self._password:
            self._login()
            headers = self._headers(kwargs.pop("headers", None))
            resp = self._session.request(
                method,
                url,
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            )

        if resp.status_code >= 400:
            detail = resp.text
            if detail and len(detail) > 1000:
                detail = detail[:1000] + "..."
            raise SisatApiError(
                f"Request failed ({resp.status_code}) {method} {path}: {detail}"
            )

        if not resp.content:
            return None
        return resp.json()

    def get_or_create_coil(
        self,
        name: str,
        metadata: Optional[dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name}
        if metadata is not None:
            payload["metadata_coil"] = metadata
        if start_time:
            payload["start_time"] = start_time
        if end_time:
            payload["end_time"] = end_time
        return self._request("POST", "/coils/get-or-create", json=payload)

    def ingest_segment(
        self,
        coil_id: int,
        cam: dict[str, Any],
        segment: dict[str, Any],
        annotators: list[dict[str, Any]],
        bboxes: list[dict[str, Any]],
        segmentations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {
            "coil_id": int(coil_id),
            "cam": cam,
            "segment": segment,
            "annotators": annotators or [],
            "bboxes": bboxes or [],
            "segmentations": segmentations or [],
        }
        return self._request("POST", "/coil-segments/ingest", json=payload)
