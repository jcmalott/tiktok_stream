import pytest
import logging
import os
import json
import requests
from unittest.mock import patch, mock_open

from backend.database import save_to_file, deep_merge, store
import backend.tests.data.test_data as test_data

TEMP_PATH = '../tests/data/temp_data.json'
DATA_PATH = '../tests/data/test_data.json'

@pytest.fixture
def set_up():
    with open(TEMP_PATH,'w', encoding='utf-8') as f:
        json.dump(test_data.OLD_DATA, f, indent=2, ensure_ascii=False)
        
    yield
    os.remove(TEMP_PATH)
    

def test_save_to_file(set_up):
    result = save_to_file(test_data.NEW_DATA, TEMP_PATH)
    assert result
    
    with open(TEMP_PATH, "r", encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data == test_data.MERGED_DATA

@pytest.mark.parametrize('old_data, new_data, merged_data',[
    (test_data.OLD_DATA, test_data.NEW_DATA, test_data.MERGED_DATA),
    (test_data.OLD_DATA_DIAMONDS, test_data.NEW_DATA_DIAMONDS, test_data.MERGED_DATA_DIAMONDS)
])    
def test_deep_merge(old_data, new_data, merged_data):
    result = deep_merge(old_data, new_data)
    assert merged_data == result
    
def test_save_to_file_with_sorting(set_up):
    # Save with sorting by visits (descending)
    result = save_to_file(test_data.NEW_DATA, TEMP_PATH, order_desc='visits')
    assert result
    
    # Read the file and verify it's sorted by visits
    with open(TEMP_PATH, "r", encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data == test_data.ORDERED_DATA

def test_save_to_empty_filepath():
    """Test save_to_file with empty filepath"""
    result = save_to_file(test_data.NEW_DATA, "")
    assert not result

def test_save_to_nonexistent_file():
    """Test save_to_file to a file that doesn't exist"""
    result = save_to_file(test_data.NEW_DATA, '../tests/data/nonexistent.json')
    assert not result

def test_store_function():
    """Test the store function directly"""
    
    # Create a file with initial data
    with open(TEMP_PATH, "w", encoding='utf-8') as f:
        json.dump({}, f)
    
    # Open the file and call store
    with open(TEMP_PATH, "r+", encoding='utf-8') as f:
        store(test_data.NEW_DATA, f, 'visits')
    
    # Read the file and verify it's correctly sorted and stored
    with open(TEMP_PATH, "r", encoding='utf-8') as f:
        stored_data = json.load(f)
        
        keys = list(stored_data.keys())
        test_keys = list(test_data.NEW_DATA.keys())
        assert keys == test_keys
        
    os.remove(TEMP_PATH)