"""Optional Azure AI Search adapter for the Phase 5 cloud retrieval mode."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

AZURE_SEARCH_API_VERSION = "2024-07-01"
DEFAULT_TIMEOUT_SECONDS = 10


class AzureSearchError(Exception):
    """Raised when optional Azure AI Search configuration or requests fail."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class AzureSearchConfig:
    """Non-secret Azure AI Search connection values read from the environment."""

    endpoint: str
    index_name: str
    api_key: str

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> AzureSearchConfig:
        """Load the required API-key configuration without exposing secret values."""
        values = os.environ if environment is None else environment
        missing = [
            name
            for name in (
                "AZURE_SEARCH_ENDPOINT",
                "AZURE_SEARCH_INDEX_NAME",
                "AZURE_SEARCH_API_KEY",
            )
            if not values.get(name, "").strip()
        ]
        if missing:
            raise AzureSearchError(
                "azure_search_configuration_missing",
                "missing required Azure AI Search environment variables: "
                + ", ".join(missing),
            )

        endpoint = values["AZURE_SEARCH_ENDPOINT"].strip().rstrip("/")
        if not endpoint.startswith("https://"):
            raise AzureSearchError(
                "invalid_azure_search_endpoint",
                "AZURE_SEARCH_ENDPOINT must use HTTPS",
            )

        return cls(
            endpoint=endpoint,
            index_name=values["AZURE_SEARCH_INDEX_NAME"].strip(),
            api_key=values["AZURE_SEARCH_API_KEY"].strip(),
        )


@dataclass(frozen=True)
class AzureSearchResult:
    """A minimal, provider-native result returned by Azure AI Search."""

    document_id: str
    score: float
    content: str


class AzureSearchClient:
    """Perform Azure AI Search keyword queries through its REST API."""

    def __init__(
        self,
        config: AzureSearchConfig,
        *,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self._config = config
        self._timeout_seconds = timeout_seconds
        self._opener = opener

    def search(self, query: str, limit: int) -> tuple[AzureSearchResult, ...]:
        """Query the configured index and adapt its minimal result fields."""
        body = json.dumps(
            {
                "search": query,
                "top": limit,
                "count": True,
                "select": "id,content",
            }
        ).encode("utf-8")
        request = Request(
            self._search_url(),
            data=body,
            headers={
                "api-key": self._config.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise AzureSearchError(
                "azure_search_request_failed",
                f"Azure AI Search returned HTTP {error.code}",
            ) from error
        except URLError as error:
            raise AzureSearchError(
                "azure_search_unavailable",
                "Azure AI Search could not be reached",
            ) from error
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AzureSearchError(
                "azure_search_invalid_response",
                "Azure AI Search returned an unreadable response",
            ) from error

        return _parse_results(payload)

    def _search_url(self) -> str:
        encoded_index = quote(self._config.index_name, safe="")
        return (
            f"{self._config.endpoint}/indexes/{encoded_index}/docs/search"
            f"?api-version={AZURE_SEARCH_API_VERSION}"
        )


def _parse_results(payload: Any) -> tuple[AzureSearchResult, ...]:
    """Validate the documented fields needed from an Azure Search response."""
    if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
        raise AzureSearchError(
            "azure_search_invalid_response",
            "Azure AI Search response must contain a value array",
        )

    results: list[AzureSearchResult] = []
    for item in payload["value"]:
        if not isinstance(item, dict):
            raise AzureSearchError(
                "azure_search_invalid_response",
                "Azure AI Search results must be JSON objects",
            )
        document_id = item.get("id")
        content = item.get("content")
        score = item.get("@search.score")
        if not isinstance(document_id, str) or not isinstance(content, str):
            raise AzureSearchError(
                "azure_search_invalid_response",
                "Azure AI Search results must include string id and content fields",
            )
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise AzureSearchError(
                "azure_search_invalid_response",
                "Azure AI Search results must include a numeric @search.score",
            )
        results.append(
            AzureSearchResult(
                document_id=document_id,
                score=float(score),
                content=content,
            )
        )
    return tuple(results)
