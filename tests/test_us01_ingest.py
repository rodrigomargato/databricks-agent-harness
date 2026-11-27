from datetime import datetime, timezone
from zipfile import ZipFile

import pandas as pd
import pytest

from src.us01_ingest import (
    DownloadError,
    add_load_metadata,
    download_to_volume,
    read_csv_chunks,
    replace_bronze_partition,
    resolve_catalog_url,
)


def test_resolve_catalog_url_selects_requested_year():
    catalog = {
        "result": {
            "resources": [
                {"name": "Contratos 2024", "url": "https://example.test/contracts-2024.zip"},
                {"name": "Contratos 2025", "url": "https://example.test/contracts-2025.zip"},
            ]
        }
    }

    assert resolve_catalog_url(catalog, 2025) == "https://example.test/contracts-2025.zip"


def test_resolve_catalog_url_rejects_missing_year():
    with pytest.raises(ValueError, match="No catalog resource found for year 2026"):
        resolve_catalog_url({"result": {"resources": []}}, 2026)


def test_download_to_volume_writes_every_chunk(tmp_path):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size):
            if getattr(self, "sent", False):
                return b""
            self.sent = True
            return b"archive-content"

    destination = tmp_path / "contracts.zip"
    result = download_to_volume(
        "https://example.test/contracts.zip",
        destination,
        lambda _: Response(),
    )
    assert result == destination
    assert destination.read_bytes() == b"archive-content"


def test_download_to_volume_returns_clear_error(tmp_path):
    def fail(_):
        raise OSError("network unavailable")

    with pytest.raises(DownloadError, match="Failed to download contracts.zip"):
        download_to_volume("https://example.test/contracts.zip", tmp_path / "contracts.zip", fail)


def test_add_load_metadata_preserves_source_fields():
    source = pd.DataFrame({"contract_id": ["A1"], "amount": ["0012,34"]})
    ingested_at = datetime(2026, 11, 27, tzinfo=timezone.utc)

    result = add_load_metadata(
        source,
        year=2025,
        source_url="https://example.test/contracts-2025.zip",
        source_date="2026-11-27",
        ingested_at=ingested_at,
    )

    assert result["contract_id"].tolist() == ["A1"]
    assert result["amount"].tolist() == ["0012,34"]
    assert result["_source_url"].tolist() == ["https://example.test/contracts-2025.zip"]
    assert result["_source_date"].tolist() == ["2026-11-27"]
    assert result["_ingested_at"].tolist() == [ingested_at]
    assert result["_load_year"].tolist() == [2025]


def test_read_csv_chunks_counts_all_rows(tmp_path):
    archive = tmp_path / "contracts.zip"
    with ZipFile(archive, "w") as output:
        output.writestr("contracts.csv", "id,value\nA,1\nB,2\nC,3\n")

    chunks = list(read_csv_chunks(archive, chunk_size=2))
    combined = pd.concat(chunks, ignore_index=True)

    assert combined.to_dict("records") == [
        {"id": "A", "value": 1},
        {"id": "B", "value": 2},
        {"id": "C", "value": 3},
    ]


def test_replace_bronze_partition_is_idempotent():
    existing = pd.DataFrame({"id": ["A"], "_load_year": [2025]})
    same_load = pd.DataFrame({"id": ["A"], "_load_year": [2025]})
    other_year = pd.DataFrame({"id": ["B"], "_load_year": [2024]})
    existing = pd.concat([existing, other_year], ignore_index=True)

    first = replace_bronze_partition(existing, same_load, 2025)
    second = replace_bronze_partition(first, same_load, 2025)

    assert first.to_dict("records") == [
        {"id": "B", "_load_year": 2024},
        {"id": "A", "_load_year": 2025},
    ]
    assert second.to_dict("records") == first.to_dict("records")
