def update_all():
    "Updates all supported entity types using merged chunk data from ingame binaries."
    from mhdata.binary import metadata
    from mhdata.binary import ItemCollection, ArmorCollection
    from mhdata.load import load_data
    
    from .armor import update_armor, update_charms
    from .weapons import update_weapons, update_weapon_songs, update_kinsects
    from .monsters import update_monsters
    from .quests import update_quests
    from .items import update_items, update_decorations, register_combinations, ItemUpdater
    from . import simple_translate

    mhdata = load_data()
    print("Existing Data loaded. Using it as a base to merge new data")

    area_map = metadata.load_area_map()
    print("Area Map Loaded")

    # validate area map
    error = False
    for name in area_map.values():
        if name not in mhdata.location_map.names('en'):
            print(f"Error: Area map has invalid location name {name}.")
            error = True
    if error:
        return
    print("Area Map validated")

    item_data = ItemCollection()
    armor_data = ArmorCollection()
    item_updater = ItemUpdater(item_data)
    monster_meta = metadata.MonsterMetadata()

    print() # newline

    simple_translate.translate_skills(mhdata)

    update_armor(mhdata, item_updater, armor_data)
    update_charms(mhdata, item_updater, armor_data)
    update_weapons(mhdata, item_updater)
    update_decorations(mhdata, item_data)
    #update_weapon_songs(mhdata)
    #update_kinsects(mhdata, item_updater)
    #update_monsters(mhdata, item_updater, monster_meta)
    #update_quests(mhdata, item_updater, monster_meta, area_map)
    
    # Now finalize the item updates from parsing the rest of the data
    register_combinations(mhdata, item_updater)
    update_items(item_updater)


def dump_file(filename):
    from . import dump as d
    import os
    
    filetypes = {
        '.gmd': d.dump_gmd
    }

    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    if extension not in filetypes:
        supported = ", ".join(filetypes.keys())
        raise Exception(f"Invalid extension {extension}, supported extensions are {supported}")

    return filetypes[extension](filename)