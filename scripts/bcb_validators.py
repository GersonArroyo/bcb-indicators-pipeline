import json
from pathlib import Path


def validate_file_exists(file):
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file}")
    if path.stat().st_size == 0:
        raise ValueError(f"Arquivo vazio: {file}")
    
    
def validate_json_format(file):
    with open(file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON no arquivo {file}: {e}")
    return data


def validate_list_of_dicts(data):
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        print(f"JSON válido com {len(data)} registros.")
    else:
        raise ValueError(f"Arquivo não contém uma lista de dicionários.")

    
def validate_has_content(data):
    if len(data) == 0:
        raise ValueError(f"Arquivo não contém dados.")
    
    
def validate_fields_values(data, required_fields):
    for item in data:
        for required_field in required_fields:
            if required_field not in item:
                raise ValueError(f"Campo obrigatório '{required_field}' ausente em uma das linhas do arquivo.")

            value = item[required_field]

            if value is None:
                raise ValueError(f"Campo obrigatório '{required_field}' está vazio em uma das linhas do arquivo.")

            if isinstance(value, str) and value.strip() == "":
                raise ValueError(f"Campo obrigatório '{required_field}' contém apenas espaços em branco em uma das linhas do arquivo.")
            

