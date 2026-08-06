from airflow.sdk import DAG
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from scripts.fetch_bcb import _json_downloader
from scripts.transform_bcb import _json_to_csv


with DAG(
    dag_id="projeto-bcb",
    start_date=datetime(2026,1,1),
    schedule='0 7 * * *',
    catchup=False
):
    fetch_bcb_series = PythonOperator(
        task_id="fetch_bcb_series",
        python_callable=_json_downloader,
        op_kwargs={
            "url":"https://api.bcb.gov.br/dados/serie/bcdata.sgs.27790/dados?formato=json",
            "output_path":"/tmp/data/raw/bcb/{{ ds }}.json"
        }
    )

    transform_to_csv = PythonOperator(
        task_id="transform_to_csv",
        python_callable=_json_to_csv,
        op_kwargs={
            "input_path":"/tmp/data/raw/bcb/{{ ds }}.json",
            "output_path":"/tmp/data/processed/bcb/{{ ds }}.csv"
        }
    )
    
    fetch_bcb_series >> transform_to_csv
    