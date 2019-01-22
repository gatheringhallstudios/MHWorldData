from mhdata.io import create_writer, DataMap
from mhdata.load import load_data, schema
from mhdata.build import datafn

from mhw_armor_edit.ftypes import wp_dat, wp_dat_g, wep_wsl, sh_tbl, bbtbl
from .load import load_schema, load_text, ItemTextHandler, SharpnessDataReader, WeaponDataLoader, convert_recipe
from .items import add_missing_items

from mhdata import cfg

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

deviation = ["None", "Low", "Average", "High"]
special_ammo_types = ["Wyvernblast", "Wyvernheart", "Wyvernsnipe"]

bullet_types = [
    "normal1", "normal2", "normal3", "pierce1", "pierce2", "pierce3",
    "spread1", "spread2", "spread3", "sticky1", "sticky2", "sticky3",
    "cluster1", "cluster2", "cluster3", "recover1", "recover2",
    "poison1", "poison2", "paralysis1", "paralysis2", "sleep1", "sleep2",
    "exhaust1", "exhaust2", "flaming", "water", "freeze", "thunder", "dragon",
    "slicing", "wyvern", "demon", "armor", "tranq"
]

# Listing of which ammo starting types do not have rapid
# This will eventually be reduced in size
not_rapid = [
    'sticky', 'cluster',
    'recover', 'poison', 'paralysis', 'sleep', 'slicing',
    'dragon', 'demon', 'armor', 'tranq', 'wyvern']

def ammotype_has_rapid(ammo_type: str):
    for val in not_rapid:
        if ammo_type.startswith(val):
            return False
    return True

class WeaponAmmoLoader():
    def __init__(self):
        self.shell_data = load_schema(sh_tbl.ShlTbl, "common/equip/shell_table.shl_tbl")
    
        self.data = {}

    def _rapid_and_recoil_from_binary_recoil(self, val: int):
        # hardcoded because mhw is weird
        # inconsistencies with source data (21 is actually recoil 4, not recoil 3)
        if val == 0:
            return (False, 1)
        if val == 18:
            return (False, 1) # Mortar
        if val == 10:
            return (False, -1) # auto-reload/singleshot
        if val in (1, 2, 3):
            return (False, 2)
        if val in (14, 27):
            return (False, 2) # Mortar
        if val in (4, 5, 7, 11, 20, 24, 32):
            return (False, 3)
        if val in (15, 16, 22, 23, 26):
            return (False, 3) # Mortar
        if val in (6, 8, 9, 12, 13, 19, 21, 25):
            return (False, 4)
        if val in (28, 29, 30):
            return (True, 2)
        if val in (31, 33):
            return (True, 3)
        if val == 17:
            return (False, 0) # probably 17 (wyvern)
        raise Exception("Unexpected value " + str(val))

    def _reload_from_binary_reload(self, val: int):
        if val == 17:
            return 'fast'
        if val in (0, 1, 14, 18):
            return 'normal'
        if val in (2, 3, 4, 5, 11, 15, 16):
            return 'slow'
        if val in (6, 7, 8, 9, 10, 12, 13):
            return 'very slow'
        return None

    def create_data_for(self, wtype: str, tree: str, binary: wp_dat_g.WpDatGEntry):
        shell = self.shell_data[binary.shell_table_id]
        
        data = {
            'deviation': deviation[binary.deviation],
            'special': special_ammo_types[binary.special_ammo_type]
        }

        for btype in bullet_types:
            clip_size = getattr(shell, f'{btype}_capacity')
            
            if clip_size:
                recoil_b = getattr(shell, f'{btype}_recoil')
                reload_b = getattr(shell, f'{btype}_reload')
                (rapid, recoil) = self._rapid_and_recoil_from_binary_recoil(recoil_b)
                reload = self._reload_from_binary_reload(reload_b)
            else:
                rapid = False
                recoil = None
                reload = None

            data[btype] = {
                'clip': getattr(shell, f'{btype}_capacity')
            }
            if ammotype_has_rapid(btype):
                data[btype]['rapid'] = rapid
            if btype != 'wyvern':
                data[btype]['recoil'] = recoil
            data[btype]['reload'] = reload

        type_short = "LBG" if wtype == cfg.LIGHT_BOWGUN else "HBG"
        tree = tree.replace(" Tree", "").replace(" Element", "")
        name = type_short + " " + tree
        
        for i in range(1, 1000):
            test_name = name if i == 1 else name + " " + str(i)
            
            if test_name not in self.data:
                self.data[test_name] = data
                return (test_name, data)
            elif self.data[test_name] == data:
                return (test_name, data)
                
        raise Exception("No suitable name found")


def update_weapons():
    mhdata = load_data()
    print("Existing Data loaded. Using to update weapon info")

    weapon_loader = WeaponDataLoader()
    item_text_handler = ItemTextHandler()
    notes_data = load_schema(wep_wsl.WepWsl, "common/equip/wep_whistle.wep_wsl")
    sharpness_reader = SharpnessDataReader()
    ammo_reader = WeaponAmmoLoader()
    coating_data = load_schema(bbtbl.Bbtbl, "common/equip/bottle_table.bbtbl")

    print("Loaded initial weapon binary data data")

    def bind_basic_weapon_data(weapon_type, existing_entry, binary):
        "Binds the basic general weapon data, plus elements"
        multiplier = cfg.weapon_multiplier[weapon_type]

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

    for weapon_type in cfg.weapon_types:
        print(f"Processing {weapon_type}")

        # Note: weapon data ordering is unknown. order field and tree_id asc are sometimes wrong
        # Therefore its unsorted, we have to work off the spreadsheet order 
        weapon_tree = weapon_loader.load_tree(weapon_type)
        print(f"Loaded {weapon_type} weapon tree binary data")

        for weapon_node in weapon_tree:
            binary = weapon_node.binary
            name = weapon_node.name
            existing_entry = mhdata.weapon_map.entry_of('en', name['en'])
            
            # For now, this routine is update only
            if not existing_entry:
                continue
            
            # Bind name and parent
            existing_entry['name'] = name
            existing_entry['weapon_type'] = weapon_type
            existing_entry['previous_en'] = None
            if weapon_node.parent != None:
                existing_entry['previous_en'] = weapon_node.parent.name['en']

            # Bind info
            bind_basic_weapon_data(weapon_type, existing_entry, binary)
            if weapon_type in cfg.weapon_types_melee:
                bind_weapon_blade_ext(weapon_type, existing_entry, binary)
                existing_entry['sharpness'] = sharpness_reader.sharpness_for(binary)
            elif weapon_type in cfg.weapon_types_gun:
                (ammo_name, ammo_data) = ammo_reader.create_data_for(
                    wtype=weapon_type, 
                    tree=weapon_node.tree,
                    binary=weapon_node.binary)
                existing_entry['ammo_config'] = ammo_name
            else:
                # TODO: Bows have an Enabled+ flag. Find out what it means
                # 1 = enabled, 2 = enabled+
                coating_binary = coating_data[binary.special_ammo_type]
                existing_entry['bow'] = {
                    'close': coating_binary.close_range > 0,
                    'power': coating_binary.power > 0,
                    'paralysis': coating_binary.paralysis > 0,
                    'poison': coating_binary.poison > 0,
                    'sleep': coating_binary.sleep > 0,
                    'blast': coating_binary.blast > 0
                }

            # crafting data
            existing_entry['craft'] = []
            if weapon_node.craft:
                existing_entry['craft'].append({
                    'type': 'Create',
                    **convert_recipe(item_text_handler, weapon_node.craft)
                })
            if weapon_node.upgrade:
                existing_entry['craft'].append({
                    'type': 'Upgrade',
                    **convert_recipe(item_text_handler, weapon_node.upgrade)
                })

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
        "weapons/weapon_bow_ext.csv",
        mhdata.weapon_map,
        key="bow",
        schema=schema.WeaponBowSchema()
    )

    writer.save_data_csv(
        "weapons/weapon_craft.csv",
        mhdata.weapon_map, 
        key="craft",
        schema=schema.WeaponCraftSchema()
    )

    writer.save_keymap_csv(
        "weapons/weapon_ammo.csv",
        ammo_reader.data,
        schema=schema.WeaponAmmoSchema()
    )

    add_missing_items(item_text_handler.encountered, mhdata=mhdata)
