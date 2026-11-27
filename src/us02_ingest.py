"""Utilities for the US02 CPV Bronze ingestion."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.request import urlopen

import pandas as pd


class DownloadError(RuntimeError):
    """Raised when catalog or source download fails."""


def fetch_catalog(
    catalog_url: str,
    *,
    timeout: float = 10,
    opener: Callable = urlopen,
) -> dict:
    """Fetch catalog metadata with a bounded request timeout."""
    try:
        with opener(catalog_url, timeout=timeout) as response:
            return json.loads(response.read())
    except (OSError, ValueError, TimeoutError) as exc:
        raise DownloadError(
            "Failed to fetch CPV catalog metadata: {}".format(exc)
        ) from exc


def resolve_cpv_resource(catalog: dict) -> dict:
    """Return the first catalog resource that looks like the CPV list."""
    result = catalog.get("result", catalog)
    resources = result.get("resources", [])

    for resource in resources:
        searchable = " ".join(
            str(resource.get(field, ""))
            for field in ("name", "title", "description", "id", "identifier")
        ).lower()
        if "cpv" not in searchable:
            continue

        url = (
            resource.get("url")
            or resource.get("download_url")
            or resource.get("resource_url")
        )
        if url:
            return dict(resource, url=str(url))

    raise ValueError("No CPV catalog resource found")


def download_with_retries(
    source_url: str,
    destination: str | Path,
    *,
    opener: Callable = urlopen,
    timeout: float = 10,
    max_attempts: int = 3,
    backoff_seconds: float = 0.1,
) -> Path:
    """Download a CPV source into a file with a timeout and limited retries."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max_attempts + 1):
        try:
            with opener(source_url, timeout=timeout) as response:
                with target.open("wb") as output:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
            return target
        except (OSError, RuntimeError, TimeoutError) as exc:
            target.unlink(missing_ok=True)
            if attempt == max_attempts:
                raise DownloadError(
                    "Failed to download CPV list {}: {}".format(
                        Path(source_url).name or "source", exc
                    )
                ) from exc
            time.sleep(backoff_seconds * attempt)

    raise AssertionError("unreachable")


def add_cpv_load_metadata(
    source: pd.DataFrame,
    *,
    source_url: str,
    source_date: str | None,
    ingested_at: datetime | None = None,
) -> pd.DataFrame:
    """Add Bronze metadata without changing source columns or values."""
    result = source.copy()
    result["_source_url"] = source_url
    result["_source_date"] = source_date
    result["_ingested_at"] = ingested_at or datetime.now(timezone.utc)
    return result


def replace_cpv_bronze(
    existing: pd.DataFrame | None,
    incoming: pd.DataFrame,
) -> pd.DataFrame:
    """Replace the CPV bronze snapshot without duplicate rerun rows."""
    if existing is None or existing.empty:
        result = incoming.copy()
    else:
        result = pd.concat([existing, incoming], ignore_index=True)
    return result.drop_duplicates(ignore_index=True)
