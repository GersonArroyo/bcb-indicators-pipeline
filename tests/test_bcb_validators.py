import pytest

from scripts.bcb_validators import (
    validate_has_content, validate_file_exists, validate_json_format,
    validate_list_of_dicts, validate_fields_values
)


def test_validate_has_content_with_data():
    data = [{"data": "01/01/2026", "valor": "10.5"}]

    validate_has_content(data)
    
    
def test_validate_has_content_with_empty_list():
    data = []

    with pytest.raises(ValueError):
        validate_has_content(data)
        
        
def test_validate_file_exists_with_existing_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")

    validate_file_exists(file_path)
    
    
def test_validate_file_exists_with_non_existing_file(tmp_path):
    file_path = tmp_path / "non_existing_file.txt"

    with pytest.raises(FileNotFoundError):
        validate_file_exists(file_path)
        
        
def test_validate_file_exists_empty_file(tmp_path):
    file_path = tmp_path / "empty_file.txt"
    file_path.touch()

    with pytest.raises(ValueError):
        validate_file_exists(file_path)
        
        
def test_validate_json_format_with_valid_json(tmp_path):
    file_path = tmp_path / "valid.json"
    file_path.write_text('{"chave": "valor"}')

    data = validate_json_format(file_path)
    
    assert data == {"chave": "valor"}
    
    
def test_validate_json_format_with_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text('{"chave": "valor"')

    with pytest.raises(ValueError):
        validate_json_format(file_path)
        
        
def test_validate_list_of_dicts_with_valid_data():
    data = [
        {"data": "01/01/2026", "valor": "10"},
        {"data": "02/01/2026", "valor": "11"},
    ]

    validate_list_of_dicts(data)
    
    
def test_validate_list_of_dicts_with_invalid_data():
    data = ["01/01/2026", "02/01/2026"]
    
    with pytest.raises(ValueError):
        validate_list_of_dicts(data)
        
    
def test_validate_fields_values_with_valid_data():
    data = [
        {"data": "01/01/2026", "valor": "10"},
        {"data": "02/01/2026", "valor": "11"},
    ]
    
    required_fields = ["data", "valor"]
    
    validate_fields_values(data, required_fields)
    
    
def test_validate_fields_values_with_missing_field():
    data = [
        {"data": "01/01/2026"}
    ]
    required_fields = ["data", "valor"]

    with pytest.raises(ValueError):
        validate_fields_values(data, required_fields)
        
        
def test_validate_fields_values_with_none_value():
    data = [
        {"data": "01/01/2026", "valor": None}
    ]
    required_fields = ["data", "valor"]

    with pytest.raises(ValueError):
        validate_fields_values(data, required_fields)
        
def test_validate_fields_values_with_empty_string_value():
    data = [
        {"data": "01/01/2026", "valor": "   "}
    ]
    required_fields = ["data", "valor"]

    with pytest.raises(ValueError):
        validate_fields_values(data, required_fields)