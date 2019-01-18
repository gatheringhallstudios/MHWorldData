from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema
from mhdata.build import datafn

from mhw_armor_edit.ftypes import wp_dat, wp_dat_g, wep_wsl, eq_crt, eq_cus, sh_tbl
from .load import load_schema, load_text, ItemTextHandler, SharpnessDataReader, convert_recipe
from .items import add_missing_items

from mhdata import cfg

# wp_dat files (mapping from filename -> mhwdb weapon type)
# ranged ones map to wp_dat_g instead
weapon_files = {
    cfg.GREAT_SWORD: 'l_sword',
    cfg.LONG_SWORD: 'tachi',
    cfg.SWORD_AND_SHIELD: 'sword',
    cfg.DUAL_BLADES: 'w_sword',
    cfg.HAMMER: 'hammer',
    cfg.HUNTING_HORN: 'whistle',
    cfg.LANCE: 'lance',
    cfg.GUNLANCE: 'g_lance',
    cfg.SWITCH_AXE: 's_axe',
    cfg.CHARGE_BLADE: 'c_axe',
    cfg.INSECT_GLAIVE: 'rod',
    cfg.LIGHT_BOWGUN: 'lbg',
    cfg.HEAVY_BOWGUN: 'hbg',
    cfg.BOW: 'bow'
}

# A list of weapon types ordered by ingame ordering. 
# Positioning here corresponds to equip type
weapon_types = [
    cfg.GREAT_SWORD, cfg.SWORD_AND_SHIELD, cfg.DUAL_BLADES, cfg.LONG_SWORD,
    cfg.HAMMER, cfg.HUNTING_HORN, cfg.LANCE, cfg.GUNLANCE, cfg.SWITCH_AXE,
    cfg.CHARGE_BLADE, cfg.INSECT_GLAIVE, cfg.BOW, cfg.HEAVY_BOWGUN, cfg.LIGHT_BOWGUN
]

elements = [
    "",
    "Fire",
    "Water",
    "Ice",
    "Thunder",
    "Dragon",
    "Poison",
    "Paralysis",
    "Sleep",
    "Blast"
]

elderseal = ["", "low", "average", "high"]

# Mapping from wep1_id to cb phial type
cb_phials = ['impact', 'power element']

# Mapping from wep1_id to saxe phial type (obtained via trial and error)
s_axe_phials = {
    0: ('power', None),
    1: ('power element', None),
    6: ('dragon', 300),
    8: ('dragon', 420),
    13: ('exhaust', 120),
    14: ('exhaust', 150),
    15: ('exhaust', 180),
    16: ('exhaust', 210),
    23: ('paralysis', 180),
    24: ('paralysis', 210),
    25: ('paralysis', 240),
    26: ('paralysis', 270),
    36: ('poison', 300),
    38: ('poison', 420)
}

# wep1_id to glaive boost type mapping
glaive_boosts = ['sever', 'blunt', 'element', 'speed', 'stamina', 'health']

# Note index to color mapping
note_colors = ['P', 'R', 'O', 'Y', 'G', 'B', 'C', 'W']

def update_weapons():
    mhdata = load_data()
    print("Existing Data loaded. Using to update weapon info")

    item_text_handler = ItemTextHandler()
    notes_data = load_schema(wep_wsl.WepWsl, "common/equip/wep_whistle.wep_wsl")
    sharpness_reader = SharpnessDataReader()

    crafting_data_map = {}
    for entry in load_schema(eq_crt.EqCrt, "common/equip/weapon.eq_crt").entries:
        wtype = weapon_types[entry.equip_type]
        crafting_data_map[(wtype, entry.equip_id)] = entry

    upgrade_data_map = {}
    for entry in load_schema(eq_cus.EqCus, "common/equip/weapon.eq_cus").entries:
        wtype = weapon_types[entry.equip_type]
        if entry.item1_qty > 0:
            upgrade_data_map[(wtype, entry.equip_id)] = entry

    upgrading_data = load_schema(eq_cus.EqCus, "common/equip/weapon.eq_cus")

    print("Loaded initial weapon binary data data")

    # Internal helper to DRY up melee/gun weapons
    def bind_basic_weapon_data(weapon_type, existing_entry, binary):
        existing_entry['weapon_type'] = weapon_type
        existing_entry['rarity'] = binary.rarity + 1
        existing_entry['attack'] = binary.raw_damage * multiplier
        existing_entry['affinity'] = binary.affinity
        existing_entry['defense'] = binary.defense or None
        existing_entry['slot_1'] = binary.gem_slot1_lvl
        existing_entry['slot_2'] = binary.gem_slot2_lvl
        existing_entry['slot_3'] = binary.gem_slot3_lvl
        existing_entry['elderseal'] = elderseal[binary.elderseal]

        # Bind element data. Dual element ones are mapped strangely, so we skip them
        if existing_entry.name('en') in ["Twin Nails", "Fire and Ice"]:
            print(f"Skipping {existing_entry.name('en')} element data")
        else:
            hidden = binary.hidden_element_id != 0
            element_id = binary.hidden_element_id if hidden else binary.element_id
            element_atk = binary.hidden_element_damage if hidden else binary.element_damage

            existing_entry['element_hidden'] = hidden
            existing_entry['element1'] = elements[element_id]
            existing_entry['element1_attack'] = element_atk * 10 if element_atk else None
            existing_entry['element2'] = None
            existing_entry['element2_attack'] = None

        # crafting data
        existing_entry['craft'] = []
        key = (weapon_type, binary.id)
        if key in crafting_data_map:
            existing_entry['craft'].append({
                'type': 'Create',
                **convert_recipe(item_text_handler, crafting_data_map[key])
            })
        if key in upgrade_data_map:
            existing_entry['craft'].append({
                'type': 'Upgrade',
                **convert_recipe(item_text_handler, upgrade_data_map[key])
            })

    def bind_weapon_blade_ext(weapon_type: str, existing_entry, binary: wp_dat.WpDatEntry):
        for key in ['kinsect_bonus', 'phial', 'phial_power', 'shelling', 'shelling_level', 'notes']:
            existing_entry[key] = None
        if weapon_type == cfg.CHARGE_BLADE:
            existing_entry['phial'] = cb_phials[binary.wep1_id]
        if weapon_type == cfg.SWITCH_AXE:
            (phial, power) = s_axe_phials[binary.wep1_id]
            existing_entry['phial'] = phial
            existing_entry['phial_power'] = power
        if weapon_type == cfg.GUNLANCE:
            # first 5 are normals, second 5 are wide, third 5 are long
            shelling = ['normal', 'wide', 'long'][binary.wep1_id // 5]
            level = (binary.wep1_id % 5) + 1
            existing_entry['shelling'] = shelling
            existing_entry['shelling_level'] = level
        if weapon_type == cfg.INSECT_GLAIVE:
            existing_entry['kinsect_bonus'] = glaive_boosts[binary.wep1_id]
        if weapon_type == cfg.HUNTING_HORN:
            note_entry = notes_data[binary.wep1_id]
            notes = [note_entry.note1, note_entry.note2, note_entry.note3]
            notes = [str(note_colors[n]) for n in notes]
            existing_entry['notes'] = "".join(notes)
        
        # Sharpness
        existing_entry['sharpness'] = sharpness_reader.sharpness_for(binary)

    for weapon_type in cfg.weapon_types_melee:
        binary_weapon_type = weapon_files[weapon_type]
        print(f"Processing {weapon_type} ({binary_weapon_type})")

        # Note: weapon data ordering is unknown. order field and tree_id asc are sometimes wrong
        weapon_binaries = load_schema(wp_dat.WpDat, f"common/equip/{binary_weapon_type}.wp_dat").entries
        weapon_text = load_text(f"common/text/steam/{binary_weapon_type}")
        print(f"Loaded {weapon_type} binary and text data")

        multiplier = cfg.weapon_multiplier[weapon_type]

        for binary in weapon_binaries:
            name = weapon_text[binary.gmd_name_index]
            existing_entry = mhdata.weapon_map.entry_of('en', name['en'])

            # For now, this routine is update only
            if not existing_entry:
                continue

            existing_entry['name'] = name
            bind_basic_weapon_data(weapon_type, existing_entry, binary)
            bind_weapon_blade_ext(weapon_type, existing_entry, binary)

    # Process ranged weapons. These use a different schema type and different post processing
    for weapon_type in cfg.weapon_types_ranged:
        binary_weapon_type = weapon_files[weapon_type]
        print(f"Processing {weapon_type} ({binary_weapon_type})")

        weapon_binaries = load_schema(wp_dat_g.WpDatG, f"common/equip/{binary_weapon_type}.wp_dat_g").entries
        weapon_text = load_text(f"common/text/steam/{binary_weapon_type}")
        print(f"Loaded {weapon_type} binary and text data")
        
        multiplier = cfg.weapon_multiplier[weapon_type]

        for binary in weapon_binaries:
            name = weapon_text[binary.gmd_name_index]
            existing_entry = mhdata.weapon_map.entry_of('en', name['en'])

            # For now, this routine is update only
            if not existing_entry:
                continue
            
            existing_entry['name'] = name
            bind_basic_weapon_data(weapon_type, existing_entry, binary)

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "weapons/weapon_base.csv",
        mhdata.weapon_map,
        schema=schema.WeaponBaseSchema(),
        translation_filename="weapons/weapon_base_translations.csv"
    )

    writer.save_data_csv(
        "weapons/weapon_sharpness.csv",
        mhdata.weapon_map, 
        key="sharpness",
        schema=schema.WeaponSharpnessSchema()
    )

    writer.save_data_csv(
        "weapons/weapon_craft.csv",
        mhdata.weapon_map, 
        key="craft",
        schema=schema.WeaponCraftSchema()
    )

    add_missing_items(item_text_handler.encountered, mhdata=mhdata)
