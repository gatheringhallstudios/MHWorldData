def update_all():
    "Updates all supported entity types using merged chunk data from ingame binaries."
    from .items import ItemUpdater
    from mhdata.load import load_data
    from mhdata.merge.binary.load import MonsterMetadata
    
    from .armor import update_armor
    from .weapons import update_weapons, update_weapon_songs, update_kinsects
    from .monsters import update_monsters
    from .quests import update_quests

    from mhdata.io.csv import read_csv
    from os.path import dirname, abspath

    this_dir = dirname(abspath(__file__))
    area_map = {int(r['id']):r['name'] for r in read_csv(this_dir + '/area_map.csv')}

    mhdata = load_data()
    print("Existing Data loaded. Using it as a base to merge new data")

    item_updater = ItemUpdater()
    monster_meta = MonsterMetadata()

    update_armor(mhdata, item_updater)
    update_weapons(mhdata, item_updater)
    update_weapon_songs(mhdata)
    update_kinsects(mhdata, item_updater)
    update_monsters(mhdata, item_updater, monster_meta)
    update_quests(mhdata, item_updater, monster_meta, area_map)
    
    # Now finalize the item updates from parsing the rest of the data
    item_updater.update_items()