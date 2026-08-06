import json
import pandas as pd
from pathlib import Path

def _json_to_csv(input_path,output_path):
    with open(input_path) as f:
        data = json.load(f)
    
    dataframe = pd.DataFrame(data)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    dataframe.to_csv(output_path, index=False)