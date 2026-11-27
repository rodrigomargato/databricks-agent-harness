# US02 - códigos CPV na bronze

## Objetivo

Ingerir a lista de códigos CPV publicada no dados.gov.pt sem duplicar dados em execuções repetidas.

## Fonte

O endereço da lista vem da resposta da API do catálogo. O módulo não fixa uma URL do ficheiro no código.

## Comportamento

- Consultas ao catálogo e downloads usam limite de tempo.
- Um download falha após três tentativas.
- Os campos da fonte são preservados.
- Metadados `_source_url`, `_source_date` e `_ingested_at` identificam a carga.
- O bronze remove linhas duplicadas ao substituir ou conciliar a lista.

## Implementação

A lógica de catálogo, download e deduplicação está em `src/us02_ingest.py` e é coberta por testes pequenos em `tests/test_us02_ingest.py`.
