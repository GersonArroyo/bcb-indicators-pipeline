from datetime import datetime, timedelta
import requests
import json
from pathlib import Path
import argparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def to_bcb_date(ds):
    return datetime.strptime(ds, "%Y-%m-%d").strftime("%d/%m/%Y")


def get_start_date_by_frequency(end_date, frequency):
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    if frequency == "monthly":
        start = end - timedelta(days=120)
    else:
        start = end - timedelta(days=10)
        
    return start.strftime("%d/%m/%Y")


def create_retry_session():
    retry_strategy = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)

    return session


def json_downloader(series_path, url, output_path, end_date):
    
    final_date = to_bcb_date(end_date)
    
    output_base_path = Path(output_path)
    
    with open(series_path, 'r', encoding='utf-8') as f:
        series_list = json.load(f)
    
    session = create_retry_session()
    
    for series in series_list:
        
        series_code = series['series_code']
        frequency = series['frequency']
        
        initial_date = get_start_date_by_frequency(end_date, frequency)
        
        series_url = f"{url}{series_code}/dados"
        
        params = {
            "formato": "json",
            "dataInicial": initial_date,
            "dataFinal": final_date
        }
        
        try:
            print(f"Buscando série {series_code}")
            print(f"URL base: {series_url}")
            print(f"Parâmetros: {params}")
            
            response = session.get(
                series_url, 
                params=params, 
                timeout=(5, 30)
            )
            
            print(f"Buscando série {series['series_code']}: {response.url}")
            print(f"Status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
        
        except requests.exceptions.RequestException:
            print(f"Erro ao buscar série {series_code}")
            print(f"URL base: {series_url}")
            print(f"Parâmetros: {params}")
            raise

        file_path = output_base_path / str(series_code) / f"{end_date}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--series_path", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--end_date", required=True)

    args = parser.parse_args()

    json_downloader(
        series_path=args.series_path,
        url=args.url,
        output_path=args.output_path,
        end_date=args.end_date
    )