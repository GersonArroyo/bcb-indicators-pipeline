
## Projeto: Pipeline de Indicadores Econômicos do Brasil
A ideia é simples: coletar séries temporais públicas do Banco Central, salvar histórico, tratar os dados e expor uma tabela final para análise.
O Banco Central disponibiliza dados do SGS/BCData em JSON, inclusive com endpoint para recuperar últimos valores de uma série.

[Fonte: Data.gov.br](https://dados.gov.br/dados/conjuntos-dados/27790-sgs)
https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json&dataInicial=07/08/2016&dataFinal=07/08/2026


## Objetivo
Criar uma pipeline Airflow que rode todo dia e atualize indicadores como:
- SELIC
- IPCA
- Dólar
- CDI
- IGP-M


## Indicadores utilizados
Este projeto não tem objetivo de fazer análise econômica avançada. O foco é construir uma pipeline de dados para coletar, transformar e armazenar séries temporais públicas.
Cada série possui:
- código SGS
- nome do indicador
- frequência
- unidade de medida
- fonte
A DAG roda diariamente.
As séries diárias são buscadas com uma janela móvel de 10 dias.
As séries mensais são buscadas com uma janela maior de 120 dias.
A tabela final usa `series_code` + `reference_date` como chave única para evitar registro duplicado.
Essa janela móvel serve pra dá mais segurança contra atraso/correção de dados.

## Tabela
Schema: public
Tabela: 
Campos:
```TEXT
id               serie
series_code      inteiro
series_name      varchar
reference_date   data
indicator_value  decimal
ingestion_date   data/hora de carga
```

## Arquitetura
O Airflow foi usado apenas como camada de orquestração. As etapas de extração e carga são executadas em containers isolados, tornando o pipeline mais próximo de um ambiente produtivo.

## Modelo do projeto
```BASH
bcb-indicators-pipeline/
├── config_bcb/
│   └── seris.json
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
