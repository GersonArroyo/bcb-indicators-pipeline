import json
from pathlib import Path

import pandas as pd


def json_to_csv(series_path, input_base_path, output_base_path, partition_date):
    with open(series_path, "r", encoding="utf-8") as f:
        series_list = json.load(f)

    for series in series_list:
        series_code = series["series_code"]
        series_name = series["series_name"]

        input_path = Path(input_base_path) / str(series_code) / f"{partition_date}.json"
        output_path = Path(output_base_path) / str(series_code) / f"{partition_date}.csv"

        if not input_path.exists():
            print(f"Arquivo não encontrado para série {series_code}: {input_path}")
            continue

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        df["series_code"] = series_code
        df["series_name"] = series_name
        df["reference_date"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
        df["value"] = pd.to_numeric(df["valor"], errors="coerce")

        df = df[["series_code", "series_name", "reference_date", "value"]]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"Série {series_code} transformada em {output_path}")