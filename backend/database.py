import json
from pathlib import Path
from collections import OrderedDict
            
def save_to_file(data, filepath: str, order_desc=''):
    if filepath == "":
        return False
    
    try:
        file_path = Path(filepath)
        
        with open(file_path, "r+", encoding='utf-8') as f:
            file_data = get_file_data(f)
            updated_data = deep_merge(file_data, data)
            store(updated_data, f, order_desc)
        return True
    except TypeError as e:
        print(f"Error: Object is not JSON serializable - {str(e)}")
        raise
    except Exception as e:
        print(f"Error saving to JSON file: {str(e)}")
        return False
        
def deep_merge(old_data: dict, new_data: dict) -> dict:
    result = old_data.copy()
    
    for key, value in new_data.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            if key == "visits":
                result[key] += 1
            elif key == "diamonds":
                result[key] += value
            else:
                result[key] = value
            
    return result
   
def get_file_data(file):
    file_data = file.read()
    if len(file_data) > 0:
        data = json.loads(file_data)
    else:
        data = dict()
        
    return data
            
def store(data, file, order_desc):
    sorted_dict = data
    if order_desc != '':
        sorted_dict = dict(sorted(data.items(), key=lambda x: x[1][order_desc], reverse=True))
    file.seek(0)
    file.write(json.dumps(sorted_dict, indent=2, ensure_ascii=False))
    file.truncate()  
        
# def clear_files(location, files):
#     for file in files:
#         with open(f'{location}/{file}.json', "w", encoding='utf-8') as clear_file:
#             clear_file.truncate()
        