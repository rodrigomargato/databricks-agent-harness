# Databricks notebook source

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd
from openpyxl import load_workbook
from pyspark.sql import functions as F

dbutils = globals()["dbutils"]
spark = globals()["spark"]


class DownloadError(RuntimeError):
    pass


def fetch_catalog(url):
    try:
        with urlopen(url) as response:
            return json.loads(response.read())
    except (OSError, ValueError) as exc:
        raise DownloadError("Failed to fetch catalog metadata: {}".format(exc)) from exc


def resolve_catalog_resource(catalog, year):
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
                return dict(resource, url=str(url))
    raise ValueError("No catalog resource found for year {}".format(year))


def download_to_volume(source_url, destination, chunk_size=1024 * 1024):
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(source_url) as response:
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


def read_csv_chunks(archive_path, chunk_size=100_000):
    with ZipFile(archive_path) as probe:
        members = probe.namelist()
    if "[Content_Types].xml" in members and "xl/workbook.xml" in members:
        yield from read_xlsx_chunks(archive_path, chunk_size)
        return

    with ZipFile(archive_path) as archive:
        csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if not csv_members:
        raise ValueError("Source archive contains no CSV file")
    with ZipFile(archive_path) as archive:
        with archive.open(csv_members[0]) as csv_file:
            yield from pd.read_csv(
                csv_file,
                chunksize=chunk_size,
                dtype=str,
                keep_default_na=False,
                low_memory=False,
            )


def read_xlsx_chunks(archive_path, chunk_size=100_000):
    with open(archive_path, "rb") as workbook_file:
        workbook = load_workbook(workbook_file, read_only=True, data_only=True)
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = [str(value) for value in next(rows)]
        buffer = []
        for row in rows:
            values = ["" if value is None else str(value) for value in row]
            buffer.append(dict(zip(headers, values)))
            if len(buffer) == chunk_size:
                yield pd.DataFrame(buffer)
                buffer = []
        if buffer:
            yield pd.DataFrame(buffer)
        workbook.close()


def add_load_metadata(source, year, source_url, source_date):
    result = source.copy()
    result["_source_url"] = source_url
    result["_source_date"] = source_date
    result["_ingested_at"] = datetime.now(timezone.utc)
    result["_load_year"] = year
    return result

dbutils.widgets.text("catalog_url", "")
dbutils.widgets.text("contracts_year", "2025")
dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("bronze_schema", "contratos_pt")
dbutils.widgets.text("landing_volume", "landing")

catalog_url = dbutils.widgets.get("catalog_url")
contracts_year = int(dbutils.widgets.get("contracts_year"))
catalog_name = dbutils.widgets.get("catalog")
bronze_schema = dbutils.widgets.get("bronze_schema")
landing_volume = dbutils.widgets.get("landing_volume")

catalog = fetch_catalog(catalog_url)
resource = resolve_catalog_resource(catalog, contracts_year)
source_url = resource["url"]
source_date = (
    resource.get("source_date")
    or resource.get("modified")
    or resource.get("publication_date")
)

archive_path = (
    f"/Volumes/{catalog_name}/{bronze_schema}/{landing_volume}/"
    f"contracts_{contracts_year}.zip"
)
download_to_volume(source_url, archive_path)

table_name = f"{catalog_name}.{bronze_schema}.bronze_contracts"
source_count = 0


for pandas_chunk in read_csv_chunks(archive_path):
    metadata_chunk = add_load_metadata(
        pandas_chunk,
        year=contracts_year,
        source_url=source_url,
        source_date=str(source_date) if source_date is not None else None,
    )
    spark_chunk = spark.createDataFrame(metadata_chunk)
    spark_chunk = spark_chunk.withColumn("_ingested_at", F.to_timestamp("_ingested_at"))

    if source_count == 0:
        spark_chunk.write.format("delta").mode("overwrite").option(
            "replaceWhere", f"_load_year = {contracts_year}"
        ).saveAsTable(table_name)
    else:
        spark_chunk.write.format("delta").mode("append").saveAsTable(table_name)

    source_count += len(pandas_chunk)

if source_count == 0:
    raise RuntimeError("The source CSV contains no rows")

bronze_count = spark.table(table_name).where(
    F.col("_load_year") == contracts_year
).count()

if bronze_count != source_count:
    raise RuntimeError(
        f"Row count mismatch: source CSV has {source_count} rows, "
        f"Bronze has {bronze_count} rows"
    )

dbutils.jobs.taskValues.set("source_count", source_count)
dbutils.jobs.taskValues.set("bronze_count", bronze_count)
