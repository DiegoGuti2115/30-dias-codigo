"""Unit and integration-style tests for the optional Azure AI Search adapter."""

from __future__ import annotations

from collections.abc import Mapping
import io
import json
from urllib.error import HTTPError, URLError

import pytest

from keyword_retrieval.azure_search import (
    AzureSearchClient,
    AzureSearchConfig,
    AzureSearchError,
    AzureSearchResult,
)


class FakeResponse:
    """Minimal context-managed HTTP response for adapter tests."""

    def __init__(self, payload: object) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def configured_environment() -> Mapping[str, str]:
    return {
        "AZURE_SEARCH_ENDPOINT": "https://example.search.windows.net/",
        "AZURE_SEARCH_INDEX_NAME": "keyword-index",
        "AZURE_SEARCH_API_KEY": "test-key",
    }


def test_config_reads_required_values_and_normalizes_endpoint() -> None:
    config = AzureSearchConfig.from_environment(configured_environment())

    assert config.endpoint == "https://example.search.windows.net"
    assert config.index_name == "keyword-index"
    assert config.api_key == "test-key"


@pytest.mark.parametrize(
    "environment, code",
    [
        ({}, "azure_search_configuration_missing"),
        (
            {
                "AZURE_SEARCH_ENDPOINT": "http://example.test",
                "AZURE_SEARCH_INDEX_NAME": "index",
                "AZURE_SEARCH_API_KEY": "key",
            },
            "invalid_azure_search_endpoint",
        ),
    ],
)
def test_config_rejects_missing_or_non_https_values(environment, code) -> None:
    with pytest.raises(AzureSearchError) as error:
        AzureSearchConfig.from_environment(environment)

    assert error.value.code == code


def test_client_adapts_minimal_azure_response_and_builds_expected_request() -> None:
    captured = {}

    def opener(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data)
        captured["api_key"] = request.get_header("Api-key")
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "value": [
                    {
                        "id": "azure-optional",
                        "content": "Azure AI Search remains optional.",
                        "@search.score": 3.5,
                    }
                ]
            }
        )

    client = AzureSearchClient(
        AzureSearchConfig.from_environment(configured_environment()), opener=opener
    )

    assert client.search("azure search", 2) == (
        AzureSearchResult(
            document_id="azure-optional",
            score=3.5,
            content="Azure AI Search remains optional.",
        ),
    )
    assert captured == {
        "url": (
            "https://example.search.windows.net/indexes/keyword-index/docs/search"
            "?api-version=2024-07-01"
        ),
        "body": {
            "search": "azure search",
            "top": 2,
            "count": True,
            "select": "id,content",
        },
        "api_key": "test-key",
        "timeout": 10,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"value": [{}]},
        {"value": [{"id": "one", "content": "Text", "@search.score": "1"}]},
    ],
)
def test_client_rejects_invalid_provider_responses(payload) -> None:
    client = AzureSearchClient(
        AzureSearchConfig.from_environment(configured_environment()),
        opener=lambda request, timeout: FakeResponse(payload),
    )

    with pytest.raises(AzureSearchError) as error:
        client.search("query", 1)

    assert error.value.code == "azure_search_invalid_response"


@pytest.mark.parametrize(
    "exception, code",
    [
        (
            HTTPError("https://example.test", 401, "Unauthorized", {}, io.BytesIO()),
            "azure_search_request_failed",
        ),
        (URLError("offline"), "azure_search_unavailable"),
    ],
)
def test_client_exposes_stable_transport_errors(exception, code) -> None:
    def opener(request, timeout):
        raise exception

    client = AzureSearchClient(
        AzureSearchConfig.from_environment(configured_environment()), opener=opener
    )

    with pytest.raises(AzureSearchError) as error:
        client.search("query", 1)

    assert error.value.code == code
