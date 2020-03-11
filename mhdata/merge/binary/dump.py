from io import StringIO
from mhdata.binary.load import load_text
from mhdata.io.csv import save_csv

def dump_gmd(filename: str):
    base_name = filename
    if base_name.lower().endswith('.gmd'):
        base_name = base_name[:-8]

    gmd_data = load_text(base_name)

    rows = []
    for idx, (key, entries) in enumerate(gmd_data.keyed_entries.items()):
        rows.append({
            'index': idx,
            'key': key,
            **entries
        })

    output = StringIO()
    save_csv(rows, output)
    return output.getvalue()
    