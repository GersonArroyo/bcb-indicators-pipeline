from airflow.sdk import DAG
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from scripts.fetch_bcb import json_downloader
# from scripts.transform_bcb import json_to_csv


with DAG(
    dag_id="projeto-bcb",
    start_date=datetime(2026,1,1),
    schedule='0 7 * * *',
    catchup=False
):
    fetch_bcb_series = PythonOperator(
        task_id="fetch_bcb_series",
        python_callable=json_downloader,
        op_kwargs={
            "series_path":"/opt/airflow/config_bcb/series.json",
            "url":"https://api.bcb.gov.br/dados/serie/bcdata.sgs.",
            "output_path":"/tmp/data/raw/bcb",
            "end_date":"{{ ds }}"
        }
    )
    
    
        
    fetch_bcb_series
    