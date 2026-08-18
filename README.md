
# Pipeline de Indicadores Econômicos do Brasil
Este projeto implementa uma pipeline de dados para coletar séries temporais públicas do Banco Central do Brasil, armazenar os dados brutos em JSON e carregar uma tabela final no PostgreSQL.

O foco do projeto é demonstrar um fluxo de engenharia de dados com:
* Apache Airflow como orquestrador
* DockerOperator para execução das etapas em containers
* PostgreSQL como banco de destino
* pgAdmin para inspeção dos dados
* carga idempotente com `UPSERT`

Fonte dos dados:
* [Data.gov.br - SGS/BCData](https://dados.gov.br/dados/conjuntos-dados/27790-sgs)
* API SGS/BCB: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json`

Exemplo de endpoint:
```text
https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json&dataInicial=07/08/2016&dataFinal=07/08/2026
```

## Objetivo
Criar uma pipeline diária que coleta, valida, normaliza e armazena indicadores econômicos públicos do Banco Central.

O projeto não tem objetivo de fazer análise econômica avançada. O foco está na construção da pipeline, organização dos dados e persistência histórica em banco relacional.

## Indicadores utilizados
As séries utilizadas estão configuradas em `config_bcb/series.json`.

Atualmente o projeto coleta:
* Meta Selic definida pelo Copom
* Taxa Selic
* Dólar americano venda
* IPCA

Cada série possui:
* código SGS
* nome do indicador
* frequência
* unidade de medida

A DAG roda diariamente.
As séries diárias são buscadas com uma janela móvel de 10 dias.
As séries mensais são buscadas com uma janela maior de 120 dias.

Essa estratégia reduz o risco de perda de dados em caso de atraso, indisponibilidade temporária ou correção posterior da fonte.

## Arquitetura
O Apache Airflow é usado apenas como camada de orquestração.

As etapas de extração e carga são executadas em containers próprios por meio do `DockerOperator`. Dessa forma, a lógica do pipeline fica separada do ambiente interno do Airflow.

Fluxo geral:
```text
Airflow DAG
    ↓
DockerOperator: fetch_bcb_series
    ↓
Arquivos JSON brutos
    ↓
DockerOperator: load_postgres
    ↓
Validação + normalização + UPSERT
    ↓
PostgreSQL
```

## Estrutura principal
```text
dags/            DAG do Airflow
scripts/         scripts de extração, validação e carga
config_bcb/      configuração das séries SGS utilizadas
sql/             script de criação da tabela final
data/            arquivos JSON brutos gerados pela pipeline
pgadmin-data/    configuração inicial do pgAdmin
```

## Tabela final
**Schema**: `public`

**Tabela**: `bcb_indicators`

**Campos**:
```text
id               identificador sequencial
series_code      código SGS da série
series_name      nome do indicador
reference_date   data de referência do indicador
indicator_value  valor do indicador
ingestion_date   data/hora de carga no banco
```

A tabela usa a combinação abaixo como chave única:
```text
series_code + reference_date
```

Essa regra evita duplicidade de registros quando a DAG é executada novamente para uma mesma janela de datas.

A carga usa `ON CONFLICT DO UPDATE`, permitindo atualizar registros existentes sem duplicar linhas.

## Pré-requisitos
Antes de executar o projeto, é necessário ter instalado:
- Docker
- Docker Compose
Este projeto foi pensado para rodar em ambiente containerizado. Não é necessário criar ambiente virtual Python local para executar a pipeline.

## Configuração do ambiente
1. Crie um arquivo `.env` a partir do `.env.example`.
2. Gere uma chave para o `FERNET_KEY`:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
3. Cole o valor gerado no arquivo `.env`.

## Criação da tabela no PostgreSQL
A tabela `bcb_indicators` é criada automaticamente na primeira inicialização do banco `postgres_bcb`.
O script `sql/create_economic_indicators.sql` é montado no container PostgreSQL em:
`/docker-entrypoint-initdb.d/01_create_economic_indicators.sql`

## Build da imagem do pipeline
A imagem `bcb-pipeline` contém os scripts e dependências usados pelas tasks executadas via `DockerOperator`.
A DAG espera que a imagem `bcb-pipeline:2.0` exista localmente antes da execução.
```bash
docker build -t bcb-pipeline:2.0 .
```

## Subindo o ambiente
```bash
docker compose up -d
```
Após subir os containers, acesse o Airflow pela porta configurada no `docker-compose.yaml`. Este Compose foi adaptado a partir do modelo oficial do Airflow.

O pgAdmin também estará disponível na porta configurada no `docker-compose.yaml`.

## Executando a DAG
1. Acessar o Airflow: 
[Link_Airflow](http://localhost:8081)
2. Faça login com as credenciais locais:
usuário: `airflow`
senha: `airflow`
3. Na lista de DAGs, procure por: `projeto-bcb`
4. Ative a DAG, se ela estiver pausada.
5. Clique em Trigger DAG para executar manualmente.
6. Acompanhe as tasks:
`fetch_bcb_series`
`load_postgres`
As duas devem finalizar com status `Success`.

A task `fetch_bcb_series` coleta os dados da API do Banco Central e salva os arquivos JSON brutos.

A task `load_postgres` valida os arquivos, normaliza os registros e realiza o UPSERT no PostgreSQL.

## Verificando os dados
Acesse o PostgreSQL:
```bash
docker compose exec postgres_bcb psql -U bcb -d bcb
```

Consulte a quantidade de registros:
```sql
SELECT COUNT(*) FROM bcb_indicators;
```

Resumo por série:
```sql
SELECT
    series_code,
    series_name,
    COUNT(*) AS total_registros,
    MIN(reference_date) AS primeira_data,
    MAX(reference_date) AS ultima_data
FROM bcb_indicators
GROUP BY series_code, series_name
ORDER BY series_code;
```

## Idempotência
A pipeline foi construída para permitir reexecução segura.

Se a task de carga for executada novamente para a mesma data, os registros não são duplicados. O PostgreSQL aplica a regra de unicidade por `series_code` e `reference_date`, e o comando `ON CONFLICT DO UPDATE` atualiza os registros existentes quando necessário.

## Status do projeto
MVP funcional:

* coleta dados da API SGS/BCB
* salva JSON bruto
* valida estrutura dos arquivos
* normaliza datas e valores
* carrega dados no PostgreSQL
* evita duplicidade com UPSERT
* executa as etapas em containers via DockerOperator
* orquestra o fluxo com Apache Airflow
