from mhdata.io import DataMap, create_writer
from mhdata.binary import ToolCollection

from mhdata.load import schema

def update_tools(mhdata):
    tool_data = ToolCollection()

    new_tools = DataMap(start_id=mhdata.tool_map.max_id+1)
    for tool in tool_data.tools:
        name_en = tool.name_upgraded['en']
        existing_entry = mhdata.tool_map.entry_of('en', name_en)
        
        new_entry = {}
        if existing_entry:
            new_entry = { **existing_entry }
            
        new_entry['name'] = tool.name_upgraded
        new_entry['name_base'] = tool.name
        new_entry['description'] = tool.description
        new_entry['tool_type'] = 'booster' if 'booster' in tool.name['en'].lower() else 'mantle'
        new_entry.setdefault('duration', 0)
        new_entry.setdefault('duration_upgraded', None)
        new_entry.setdefault('recharge', 0)
        new_entry['slot_1'] = tool.slots[0]
        new_entry['slot_2'] = tool.slots[1]
        new_entry['slot_3'] = tool.slots[2]
        new_entry.setdefault('icon_color', None)

        new_tools.insert(new_entry)

    writer = create_writer()

    writer.save_base_map_csv(
        "tools/tool_base.csv",
        new_tools,
        schema=schema.ToolSchema(),
        translation_filename="tools/tool_base_translations.csv",
        translation_extra=['name_base', 'description']
    )