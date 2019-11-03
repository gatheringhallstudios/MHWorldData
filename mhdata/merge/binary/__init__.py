def update_all():
    "Updates all supported entity types using merged chunk data from ingame binaries."
    from .armor import update_armor
    from .weapons import update_weapons, update_weapon_songs, update_kinsects
    from .items import ItemUpdater
    from .monsters import update_monsters
    from .quests import update_quests
    from mhdata.load import load_data

    mhdata = load_data()
    print("Existing Data loaded. Using it as a base to merge new data")

    item_updater = ItemUpdater()
    update_armor(mhdata, item_updater)
    update_weapons(mhdata, item_updater)
    update_weapon_songs(mhdata)
    update_kinsects(mhdata, item_updater)
    update_monsters(mhdata, item_updater)
    update_quests(mhdata, item_updater)
    
    # Now finalize the item updates from parsing the rest of the data
    item_updater.update_items()