import argparse
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import psycopg
from scripts.bcb_validators import (
    validate_file_exists, 
    validate_json_format, 
    validate_list_of_dicts, 
    validate_has_content, 
    validate_fields_values)


def build_normalized_records(series_path, input_path, partition_date):
    
    with open(series_path, 'r', encoding='utf-8') as f:
        series_list = json.load(f)
    
    normalized_data = []
    
    for series in series_list:
        input_base_path = Path(input_path)
        
        series_code = series['series_code']
        series_name = series['series_name']
        file = input_base_path / str(series_code) / f"{partition_date}.json"
        
        validate_file_exists(file)
        
        data = validate_json_format(file)
        
        validate_list_of_dicts(data)
        validate_has_content(data)
        
        required_fields = ["data", "valor"]
        validate_fields_values(data, required_fields)
        
        for item in data:
            normalized_item = {
                "series_code": series_code,
                "series_name": series_name,
                "reference_date": datetime.strptime(item["data"].strip(), "%d/%m/%Y").date(),
                "indicator_value": Decimal(item["valor"].strip()),
            }
            normalized_data.append(normalized_item)
            
    return normalized_data


def save_records_to_postgres(normalized_data):

    conn = psycopg.connect(
            host="postgres_bcb",
            port=5432,
            dbname="bcb",
            user="bcb",
            password="bcb"
        )
    
    cursor = conn.cursor()
    
    for register in normalized_data:
        try:
            cursor.execute(
                """
                INSERT INTO bcb_indicators (series_code, series_name, reference_date, indicator_value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (series_code, reference_date) DO UPDATE
                SET series_name = EXCLUDED.series_name,
                    indicator_value = EXCLUDED.indicator_value;
                """,
                (register["series_code"], register["series_name"], register["reference_date"], register["indicator_value"])
            )
        except Exception as e:
            print(f"Error inserting record: {register}. Error: {e}")
            conn.rollback()
    conn.commit()
    
    
def load_bcb_to_postgres(series_path, input_path, partition_date):
    normalized_data = build_normalized_records(series_path, input_path, partition_date)
    save_records_to_postgres(normalized_data)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--series_path", required=True)
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--partition_date", required=True)

    args = parser.parse_args()

    load_bcb_to_postgres(
        series_path=args.series_path,
        input_path=args.input_path,
        partition_date=args.partition_date
    )