"""End-to-end CLI tests for Phase 5 local and Azure retrieval responses."""

from __future__ import annotations

import json

import pytest

from keyword_retrieval.main import DEFAULT_CORPUS, DEFAULT_LIMIT, VALIDATION_EXIT_CODE, main


def test_main_prints_default_retrieval_response(capsys) -> None:
    exit_code = main(["azure search"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "corpus": DEFAULT_CORPUS.as_posix(),
        "document_count": 3,
        "format": "json",
        "limit": DEFAULT_LIMIT,
        "match_count": 1,
        "normalized_terms": ["azure", "search"],
        "phase": 5,
        "query": "azure search",
        "result_count": 1,
        "results": [
            {
                "id": "azure-optional",
                "matched_terms": ["azure", "search"],
                "preview": "Azure AI Search remains optional and must never block the local workflow.",
                "score": 2,
            }
        ],
        "source": "local",
        "status": "completed",
    }


def test_main_applies_limit_to_deterministically_ranked_results(capsys) -> None:
    exit_code = main(["retrieval", "--limit", "2"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["match_count"] == 2
    assert payload["result_count"] == 2
    assert [result["id"] for result in payload["results"]] == [
        "deterministic-results",
        "local-fallback",
    ]


def test_main_returns_a_valid_empty_result_set_when_nothing_matches(capsys) -> None:
    exit_code = main(["unmatched-term"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["normalized_terms"] == ["unmatched", "term"]
    assert payload["match_count"] == 0
    assert payload["result_count"] == 0
    assert payload["results"] == []


def test_main_accepts_a_valid_custom_corpus(tmp_path, capsys) -> None:
    corpus = tmp_path / "custom-corpus.json"
    corpus.write_text(
        '[{"id": "one", "content": "Custom local content."}]', encoding="utf-8"
    )

    exit_code = main(
        [
            "LOCAL",
            "--corpus",
            corpus.as_posix(),
            "--limit",
            "3",
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["query"] == "LOCAL"
    assert payload["normalized_terms"] == ["local"]
    assert payload["corpus"] == corpus.as_posix()
    assert payload["document_count"] == 1
    assert payload["limit"] == 3
    assert payload["results"][0]["id"] == "one"


def test_main_local_fixture_covers_normalization_scoring_ties_and_limit(
    tmp_path, capsys
) -> None:
    corpus = tmp_path / "ranking-fixture.json"
    corpus.write_text(
        json.dumps(
            [
                {"id": "zeta", "content": "CAFÉ local"},
                {"id": "alpha", "content": "Café local"},
                {"id": "solo", "content": "local only"},
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "cafe LOCAL cafe",
            "--corpus",
            corpus.as_posix(),
            "--limit",
            "2",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["normalized_terms"] == ["cafe", "local"]
    assert payload["match_count"] == 3
    assert payload["result_count"] == 2
    assert payload["results"] == [
        {
            "id": "alpha",
            "score": 2,
            "matched_terms": ["cafe", "local"],
            "preview": "Café local",
        },
        {
            "id": "zeta",
            "score": 2,
            "matched_terms": ["cafe", "local"],
            "preview": "CAFÉ local",
        },
    ]


@pytest.mark.parametrize(
    ("argv", "code"),
    [
        (["   "], "invalid_query"),
        (["valid", "--limit", "0"], "invalid_limit"),
        (["valid", "--corpus", "data/missing.json"], "corpus_not_found"),
    ],
)
def test_main_preserves_stable_validation_errors(argv, code, capsys) -> None:
    exit_code = main(argv)

    captured = capsys.readouterr()
    assert exit_code == VALIDATION_EXIT_CODE
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == code


def test_main_azure_provider_serializes_a_provider_distinct_response(
    monkeypatch, capsys
) -> None:
    from keyword_retrieval.azure_search import AzureSearchResult

    monkeypatch.setattr(
        "keyword_retrieval.main.AzureSearchConfig.from_environment",
        staticmethod(lambda: type("Config", (), {"index_name": "cloud-index"})()),
    )
    monkeypatch.setattr(
        "keyword_retrieval.main.AzureSearchClient.search",
        lambda self, query, limit: (
            AzureSearchResult("cloud-document", 2.75, "Cloud Azure Search content."),
        ),
    )

    exit_code = main(["azure search", "--provider", "azure", "--limit", "1"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "format": "json",
        "index": "cloud-index",
        "limit": 1,
        "match_count": 1,
        "normalized_terms": ["azure", "search"],
        "phase": 5,
        "query": "azure search",
        "result_count": 1,
        "results": [
            {
                "id": "cloud-document",
                "preview": "Cloud Azure Search content.",
                "score": 2.75,
            }
        ],
        "source": "azure_ai_search",
        "status": "completed",
    }


def test_main_azure_provider_returns_a_stable_configuration_error(capsys) -> None:
    exit_code = main(["azure search", "--provider", "azure"])

    captured = capsys.readouterr()
    assert exit_code == VALIDATION_EXIT_CODE
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "azure_search_configuration_missing"


def test_main_rejects_unsupported_format() -> None:
    with pytest.raises(SystemExit) as error:
        main(["valid", "--format", "text"])

    assert error.value.code == 2
