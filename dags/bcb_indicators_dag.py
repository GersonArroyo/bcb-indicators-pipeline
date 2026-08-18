from airflow.sdk import DAG
from datetime import datetime, timedelta
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="projeto-bcb",
    start_date=datetime(2026,1,1),
    schedule='0 7 * * *',
    catchup=False,
    default_args={
        "retries":2,
        "retry_delay":timedelta(minutes=5)
    }
):
    fetch_bcb_series = DockerOperator(
        task_id="fetch_bcb_series",
        image="bcb-pipeline:2.0",
        command=[
            'python', \
            '-m', \
            "scripts.fetch_bcb", \
            "--series_path", "/opt/airflow/config_bcb/series.json", \
            "--url", "https://api.bcb.gov.br/dados/serie/bcdata.sgs.", \
            "--output_path", "/tmp/data/raw/bcb", \
            "--end_date", "{{ ds }}"
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="success",
        mount_tmp_dir=False,
    )
    
    load_postgres = DockerOperator(
        task_id="load_postgres",
        image="bcb-pipeline:2.0",
        command=[
            'python', \
            '-m', \
            "scripts.load_postgres", \
            "--series_path", "/opt/airflow/config_bcb/series.json", \
            "--input_path", "/tmp/data/raw/bcb", \
            "--partition_date", "{{ ds }}"
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    fetch_bcb_series >> load_postgres
    