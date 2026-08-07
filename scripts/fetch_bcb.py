from datetime import datetime, timedelta
from urllib import response
import requests
import json
from pathlib import Path

def to_bcb_date(ds):
    return datetime.strptime(ds, "%Y-%m-%d").strftime("%d/%m/%Y")

def get_start_date_by_frequency(end_date, frequency):
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if frequency == "monthly":
        start = end - timedelta(days=120)
    else:
        start = end - timedelta(days=10)

    return start.strftime("%d/%m/%Y")

def json_downloader(series_path, url, output_path, end_date):
    
    final_date = to_bcb_date(end_date)
    
    output_base_path = Path(output_path)
    
    with open(series_path, 'r', encoding='utf-8') as f:
        series_list = json.load(f)
    
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
            
            response = requests.get(
                series_url, 
                params=params, 
                timeout=10
            )
            
            print(f"Buscando série {series['series_code']}: {response.url}")
            print(f"Status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
        
        except requests.exceptions.RequestException as error:
            print(f"Erro ao buscar série {series_code}")
            print(f"URL chamada: {response.url if 'response' in locals() else series_url}")
            raise error
        
        file_path = output_base_path / str(series_code) / f"{end_date}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
