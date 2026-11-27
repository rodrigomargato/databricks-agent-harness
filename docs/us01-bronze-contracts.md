# US01: bronze contracts

The US01 ingestion resolves the 2025 contracts archive through the configured
dados.gov.pt catalog API. The catalog URL is supplied as a parameter and is never
committed to source code.

The source archive is streamed in 1 MB chunks into `/Volumes/<catalog>/<schema>/<volume>/raw`
and the CSV is read in 100,000-row chunks. Source columns are kept unchanged; US01 adds:

- `_source_url`: URL resolved from the catalog
- `_source_date`: publication date from the catalog, when supplied
- `_ingested_at`: UTC ingestion timestamp
- `_load_year`: selected year

Running the load again replaces only the selected year's partition. It does not append the
same year. Row count reconciliation compares the streamed CSV row count with the Bronze
row count.
