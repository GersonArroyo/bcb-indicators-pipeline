import json
from pathlib import Path
import pandas as pd


def validate_file_exists(file):
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file}")
    if path.stat().st_size == 0:
        raise ValueError(f"Arquivo vazio: {file}")
        
        
def validate_pattern(df: pd.DataFrame):
    if df.empty:
        raise ValueError("O DataFrame está vazio.")
    for row in df.isna().any(axis=1):
        if row:
            raise ValueError("Existem linhas com valores nulos no DataFrame.")
        
        
def validate_duplicates(df: pd.DataFrame):
    if df.duplicated(subset=["series_code", "reference_date"]).any():
        raise ValueError("Existem linhas duplicadas no DataFrame com base em 'series_code' e 'reference_date'.")
        
        
def json_to_csv(series_path, input_base_path, output_base_path, partition_date):
    with open(series_path, "r", encoding="utf-8") as f:
        series_list = json.load(f)
        
    for series in series_list:
        series_code = series["series_code"]
        series_name = series["series_name"]
        
        input_path = Path(input_base_path) / str(series_code) / f"{partition_date}.json"
        output_path = Path(output_base_path) / str(series_code) / f"{partition_date}.csv"
        
        validate_file_exists(input_path)
        
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        df = pd.DataFrame(data)
        
        df["series_code"] = series_code
        df["series_name"] = series_name
        df["reference_date"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
        df["value"] = pd.to_numeric(df["valor"], errors="coerce")
        
        df = df[["series_code", "series_name", "reference_date", "value"]]
        
        validate_pattern(df)
        validate_duplicates(df)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"Série {series_code} transformada em {output_path}")
        
        validate_file_exists(output_path)
        
