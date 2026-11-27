"""Utilities for the US01 Bronze contracts ingestion."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd


class DownloadError(RuntimeError):
    """Raised when a catalog or source download fails."""


def resolve_catalog_url(catalog: dict, year: int) -> str:
    """Return the first catalog resource URL associated with the requested year."""
    result = catalog.get("result", catalog)
    resources = result.get("resources", [])

    for resource in resources:
        searchable = " ".join(
            str(resource.get(field, ""))
            for field in ("name", "title", "description", "id", "identifier", "url")
        )
        if str(year) in searchable:
            url = (
                resource.get("url")
                or resource.get("download_url")
                or resource.get("resource_url")
            )
            if url:
                return str(url)

    raise ValueError("No catalog resource found for year {}".format(year))


def fetch_catalog(catalog_url: str, opener: Callable = urlopen) -> dict:
    """Fetch catalog metadata from a URL."""
    try:
        with opener(catalog_url) as response:
            return json.loads(response.read())
    except (OSError, ValueError) as exc:
        raise DownloadError("Failed to fetch catalog metadata: {}".format(exc)) from exc


def download_to_volume(
    source_url: str,
    destination: str | Path,
    opener: Callable = urlopen,
    chunk_size: int = 1024 * 1024,
) -> Path:
    """Stream a source archive into a Volume (or local test path)."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        with opener(source_url) as response:
            with target.open("wb") as output:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    output.write(chunk)
    except (OSError, RuntimeError) as exc:
        raise DownloadError(
            "Failed to download {}: {}".format(Path(source_url).name or "source archive", exc)
        ) from exc

    return target


def find_csv_member(archive_path: str | Path) -> str:
    """Find one CSV member in a source archive."""
    with ZipFile(archive_path) as archive:
        csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]

    if not csv_members:
        raise ValueError("Source archive contains no CSV file")
    return csv_members[0]


def read_csv_chunks(
    archive_path: str | Path,
    chunk_size: int = 100_000,
    csv_member: str | None = None,
) -> Iterator[pd.DataFrame]:
    """Read CSV rows in bounded chunks without loading the archive into memory."""
    member = csv_member or find_csv_member(archive_path)
    with ZipFile(archive_path) as archive:
        with archive.open(member) as csv_file:
            yield from pd.read_csv(csv_file, chunksize=chunk_size, low_memory=False)


def add_load_metadata(
    source: pd.DataFrame,
    *,
    year: int,
    source_url: str,
    source_date: str | None,
    ingested_at: datetime | None = None,
) -> pd.DataFrame:
    """Add Bronze load metadata without changing source columns or values."""
    result = source.copy()
    result["_source_url"] = source_url
    result["_source_date"] = source_date
    result["_ingested_at"] = ingested_at or datetime.now(timezone.utc)
    result["_load_year"] = year
    return result


def replace_bronze_partition(
    existing: pd.DataFrame | None,
    incoming: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """Replace only the selected year, making a rerun of the same year idempotent."""
    if existing is None or existing.empty:
        return incoming.copy()

    retained = existing.loc[existing["_load_year"] != year].copy()
    return pd.concat([retained, incoming.copy()], ignore_index=True)


def count_csv_rows(
    archive_path: str | Path,
    chunk_size: int = 100_000,
    csv_member: str | None = None,
) -> int:
    """Count source rows while streaming the decompressed CSV."""
    return sum(len(chunk) for chunk in read_csv_chunks(archive_path, chunk_size, csv_member))
