import json
from pathlib import Path

import pandas as pd
import pytest

from src.us02_ingest import (
    DownloadError,
    download_with_retries,
    replace_cpv_bronze,
    resolve_cpv_resource,
)


def test_resolve_cpv_resource_reads_small_catalog_fixture():
    fixture = Path(__file__).parent / "fixtures" / "cpv_catalog_small.json"
    catalog = fixture.open("r", encoding="utf-8").read()

    resource = resolve_cpv_resource(json.loads(catalog))

    assert resource["url"] == "https://example.test/cpv-list.csv"
    assert resource["source_date"] == "2026-11-27"


def test_download_with_retries_has_timeout_and_limit(tmp_path):
    attempts = []

    def fail(url, timeout):
        attempts.append((url, timeout))
        raise OSError("temporarily unavailable")

    with pytest.raises(DownloadError, match="Failed to download CPV list"):
        download_with_retries(
            "https://example.test/cpv-list.csv",
            tmp_path / "cpv.csv",
            opener=lambda url, timeout: fail(url, timeout),
            timeout=2,
            max_attempts=3,
        )

    assert attempts == [
        ("https://example.test/cpv-list.csv", 2),
        ("https://example.test/cpv-list.csv", 2),
        ("https://example.test/cpv-list.csv", 2),
    ]


def test_replace_cpv_bronze_is_idempotent():
    existing = pd.DataFrame({"code": ["1"], "_source_date": ["2026-11-27"]})
    incoming = pd.DataFrame({"code": ["1"], "_source_date": ["2026-11-27"]})

    first = replace_cpv_bronze(existing, incoming)
    second = replace_cpv_bronze(first, incoming)

    assert first.to_dict("records") == [{"code": "1", "_source_date": "2026-11-27"}]
    assert second.to_dict("records") == first.to_dict("records")
