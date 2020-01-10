def update_all():
    "Updates all supported entity types using merged chunk data from ingame binaries."
    from .items import ItemUpdater
    from mhdata.load import load_data
    from . import metadata
    
    from .armor import update_armor
    from .weapons import update_weapons, update_weapon_songs, update_kinsects
    from .monsters import update_monsters
    from .quests import update_quests

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

    item_updater = ItemUpdater()
    monster_meta = metadata.MonsterMetadata()

    print() # newline

    update_armor(mhdata, item_updater)
    update_weapons(mhdata, item_updater)
    update_weapon_songs(mhdata)
    update_kinsects(mhdata, item_updater)
    update_monsters(mhdata, item_updater, monster_meta)
    update_quests(mhdata, item_updater, monster_meta, area_map)
    
    # Now finalize the item updates from parsing the rest of the data
    item_updater.update_items()