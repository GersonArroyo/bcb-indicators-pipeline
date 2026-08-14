from airflow.sdk import DAG
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from scripts.fetch_bcb import json_downloader
from scripts.load_postgres import load_bcb_to_postgres


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
    
    load_postgres = PythonOperator(
        task_id="load_postgres",
        python_callable=load_bcb_to_postgres,
        op_kwargs={
            "series_path":"/opt/airflow/config_bcb/series.json",
            "input_path":"/tmp/data/raw/bcb",
            "partition_date":"{{ ds }}"
        }
    )
    
    test_docker_operator = DockerOperator(
        task_id="test_docker_operator",
        image="bcb-pipeline:1.0",
        command=['python', '-c', "print('container do pipeline executou')"],
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    fetch_bcb_series >> load_postgres
    