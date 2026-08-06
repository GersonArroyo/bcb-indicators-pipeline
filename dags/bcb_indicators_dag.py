from airflow.sdk import DAG
from datetime import datetime
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import Path, PythonOperator
import json
import pandas as pd
import requests


def _json_to_csv(input_path,output_path):
    with open(input_path) as f:
        data = json.load(f)
    
    dataframe = pd.DataFrame(data)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(output_path, index=False)

def _json_downloader(url, output_path):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f)

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