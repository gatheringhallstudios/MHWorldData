def update_all():
    "Updates all supported entity types using merged chunk data from ingame binaries."
    from .armor import update_armor
    from .weapons import update_weapons
    from .items import ItemUpdater

    item_updater = ItemUpdater()
    update_armor(item_updater)
    update_weapons(item_updater)
    
    item_updater.update_items()