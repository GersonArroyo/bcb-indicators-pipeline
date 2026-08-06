## Projeto: Pipeline de Indicadores Econômicos do Brasil

A ideia é simples: coletar séries temporais públicas do Banco Central, salvar histórico, tratar os dados e expor uma tabela final para análise.

O Banco Central disponibiliza dados do SGS/BCData em JSON, inclusive com endpoint para recuperar últimos valores de uma série.

[Fonte: Data.gov.br](https://dados.gov.br/dados/conjuntos-dados/27790-sgs)
https://api.bcb.gov.br/dados/serie/bcdata.sgs.27790/dados?formato=json

## Objetivo
Criar uma pipeline Airflow que rode todo dia e atualize indicadores como:
- SELIC
- IPCA
- Dólar
- CDI
- IGP-M

```BASH
bcb-indicators-pipeline/
├── dags/
│   └── bcb_indicators_dag.py
├── scripts/
│   ├── fetch_bcb.py
│   ├── transform_bcb.py
│   └── load_postgres.py
├── data/
│   ├── raw/
│   └── processed/
├── sql/
├── docker-compose.yaml
└── README.md
```
