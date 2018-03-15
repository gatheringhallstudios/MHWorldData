import json
from .config import get_languages, get_data_path

def save_translate_map(location, translate_map):
    "Writes a translate map to a location in the data directory"
    location = get_data_path(location)
    result = []
    for row in translate_map:
        entry = {}
        for lang in get_languages():
            entry['name_'+lang] = row.get(lang, "")
        result.append(entry)

    with open(location, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def save_data_map(location, data_map):
    "Write a DataMap to a location in the data directory in translatemap order"
    items = list(data_map.values())
    location = get_data_path(location)
    with open(location, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=4, ensure_ascii=False)
