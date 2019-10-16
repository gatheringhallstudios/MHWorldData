from decimal import Decimal, ROUND_HALF_UP

from mhdata.io import create_writer, DataMap
from mhdata.load import schema, datafn

from mhw_armor_edit.ftypes import wp_dat, wp_dat_g, wep_wsl, sh_tbl, bbtbl
from mhw_armor_edit.ftypes.ext import msk

from .load import load_schema, load_text, ItemTextHandler, \
                    SkillTextHandler, SharpnessDataReader, \
                    WeaponDataLoader, convert_recipe, load_kinsect_tree
from .items import ItemUpdater

from mhdata import cfg

from . import artifacts

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

kinsect_attack_types = ['Sever', 'Blunt']
kinsect_dusts = ['Blast', 'Heal', 'Paralysis', 'Poison']

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


def update_weapons(mhdata, item_updater: ItemUpdater):
    item_text_handler = ItemTextHandler()
    skill_text_handler = SkillTextHandler()

    print("Beginning load of binary weapon data")
    weapon_loader = WeaponDataLoader()
    notes_data = load_schema(wep_wsl.WepWsl, "common/equip/wep_whistle.wep_wsl")
    sharpness_reader = SharpnessDataReader()
    ammo_reader = WeaponAmmoLoader()
    coating_data = load_schema(bbtbl.Bbtbl, "common/equip/bottle_table.bbtbl")
    print("Loaded weapon binary data")

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

    # Load weapon tree binary data
    weapon_trees = {}
    for weapon_type in cfg.weapon_types:
        weapon_tree = weapon_loader.load_tree(weapon_type)
        print(f"Loaded {weapon_type} weapon tree binary data")
        weapon_trees[weapon_type] = weapon_tree

    # Write artifact lines
    print("Writing artifact files for weapons (use it to add new weapons)")
    crafted_lines = []
    isolated_lines = []
    for weapon_type, weapon_tree in weapon_trees.items():
        for weapon in weapon_tree.crafted():
            crafted_lines.append(f'{weapon.name["en"]},{weapon_type}')
        for weapon in weapon_tree.isolated():
            isolated_lines.append(f'{weapon.name["en"]},{weapon_type}')
    artifacts.write_artifact('weapons_crafted.txt', *crafted_lines)
    artifacts.write_artifact('weapons_isolated.txt', *isolated_lines)

    # Store new weapon entries
    new_weapon_map = DataMap(languages=["en"], start_id=mhdata.weapon_map.max_id+1)

    # Iterate over existing weapons, merge new data in
    for existing_entry in mhdata.weapon_map.values():
        weapon_type = existing_entry['weapon_type']
        weapon_tree = weapon_trees[weapon_type]

        # Note: weapon data ordering is unknown. order field and tree_id asc are sometimes wrong
        # Therefore its unsorted, we have to work off the spreadsheet order
        multiplier = cfg.weapon_multiplier[weapon_type]

        weapon_node = weapon_tree.by_name(existing_entry.name('en'))
        if not weapon_node:
            print(f"Could not find binary entry for {existing_entry.name('en')}")
            new_weapon_map.insert(existing_entry)
            continue
            
        is_kulve = (existing_entry['category'] == 'Kulve')
        binary = weapon_node.binary
        name = weapon_node.name

        new_entry = { **existing_entry }
        
        # Bind name and parent
        new_entry['name'] = name
        new_entry['weapon_type'] = weapon_type
        new_entry['previous_en'] = None
        if weapon_node.parent != None:
            new_entry['previous_en'] = weapon_node.parent.name['en']

        # Bind info
        new_entry['weapon_type'] = weapon_type
        new_entry['rarity'] = binary.rarity + 1
        new_entry['attack'] = (binary.raw_damage * multiplier).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        new_entry['affinity'] = binary.affinity
        new_entry['defense'] = binary.defense or None
        new_entry['slot_1'] = binary.gem_slot1_lvl
        new_entry['slot_2'] = binary.gem_slot2_lvl
        new_entry['slot_3'] = binary.gem_slot3_lvl
        new_entry['elderseal'] = elderseal[binary.elderseal]

        # Bind Elements
        if name['en'] in ["Twin Nails", "Fire and Ice"]:
            print(f"Skipping {name['en']} element data")
        else:
            hidden = binary.hidden_element_id != 0
            element_id = binary.hidden_element_id if hidden else binary.element_id
            element_atk = binary.hidden_element_damage if hidden else binary.element_damage

            new_entry['element_hidden'] = hidden
            new_entry['element1'] = elements[element_id]
            new_entry['element1_attack'] = element_atk * 10 if element_atk else None
            new_entry['element2'] = None
            new_entry['element2_attack'] = None

        # Bind skill
        skill = skill_text_handler.get_skilltree_name(binary.skill_id)
        new_entry['skill'] = skill['en'] if binary.skill_id != 0 else None
        
        # Bind Extras (Blade/Gun/Bow data)
        if weapon_type in cfg.weapon_types_melee:
            bind_weapon_blade_ext(weapon_type, new_entry, binary)
            new_entry['sharpness'] = sharpness_reader.sharpness_for(binary)
        elif weapon_type in cfg.weapon_types_gun:
            tree = weapon_node.tree
            if is_kulve:
                tree = 'Kulve'
            (ammo_name, ammo_data) = ammo_reader.create_data_for(
                wtype=weapon_type, 
                tree=tree,
                binary=weapon_node.binary)
            new_entry['ammo_config'] = ammo_name
        else:
            # TODO: Bows have an Enabled+ flag. Find out what it means
            # 1 = enabled, 2 = enabled+
            coating_binary = coating_data[binary.special_ammo_type]
            new_entry['bow'] = {
                'close': coating_binary.close_range > 0,
                'power': coating_binary.power > 0,
                'paralysis': coating_binary.paralysis > 0,
                'poison': coating_binary.poison > 0,
                'sleep': coating_binary.sleep > 0,
                'blast': coating_binary.blast > 0
            }

        # crafting data
        new_entry['craft'] = []
        if weapon_node.craft:
            new_entry['craft'].append({
                'type': 'Create',
                **convert_recipe(item_text_handler, weapon_node.craft)
            })
        if weapon_node.upgrade:
            new_entry['craft'].append({
                'type': 'Upgrade',
                **convert_recipe(item_text_handler, weapon_node.upgrade)
            })

        new_weapon_map.insert(new_entry)

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "weapons/weapon_base.csv",
        new_weapon_map,
        schema=schema.WeaponBaseSchema(),
        translation_filename="weapons/weapon_base_translations.csv"
    )

    writer.save_data_csv(
        "weapons/weapon_sharpness.csv",
        new_weapon_map, 
        key="sharpness",
        schema=schema.WeaponSharpnessSchema()
    )

    writer.save_data_csv(
        "weapons/weapon_bow_ext.csv",
        new_weapon_map,
        key="bow",
        schema=schema.WeaponBowSchema()
    )

    writer.save_data_csv(
        "weapons/weapon_craft.csv",
        new_weapon_map, 
        key="craft",
        schema=schema.RecipeUpgradeSchema()
    )

    writer.save_keymap_csv(
        "weapons/weapon_ammo.csv",
        ammo_reader.data,
        schema=schema.WeaponAmmoSchema()
    )

    print("Weapon files updated\n")

    item_updater.add_missing_items(item_text_handler.encountered)

def update_kinsects(mhdata, item_updater):
    item_text_handler = ItemTextHandler()
    
    print('Loading kinsect info')

    kinsect_tree = load_kinsect_tree()

    def resolve_parent_name(entry):
        if entry.parent:
            return entry.parent.name['en']
        return ''

    items = [f"{r.id},{r.name['en']},{resolve_parent_name(r)}" for r in kinsect_tree.crafted()]
    artifacts.write_artifact('kinsect_all.txt', *items)
    items = [f"{r.id},{r.name['en']}" for r in kinsect_tree.roots]
    artifacts.write_artifact('kinsect_roots.txt', *items)

    kinsect_map = DataMap(languages=['en'])
    for kinsect_node in kinsect_tree.crafted():
        binary = kinsect_node.binary
        new_entry = kinsect_map.insert({
            'id': binary.id + 1,
            'name': kinsect_node.name,
            'previous_en': resolve_parent_name(kinsect_node),
            'rarity': binary.rarity + 1,
            'attack_type': kinsect_attack_types[binary.attack_type],
            'dust_effect': kinsect_dusts[binary.dust_type],
            'power': binary.power,
            'speed': binary.speed,
            'heal': binary.heal
        })

        if kinsect_node.upgrade:
            new_entry['craft'] = convert_recipe(item_text_handler, kinsect_node.upgrade)

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "weapons/kinsect_base.csv",
        kinsect_map,
        schema=schema.KinsectBaseSchema(),
        translation_filename="weapons/kinsect_base_translations.csv"
    )

    writer.save_data_csv(
        "weapons/kinsect_craft_ext.csv",
        kinsect_map, 
        key="craft",
        schema=schema.RecipeSchema()
    )
    
    print("Kinsect files updated\n")
    item_updater.add_missing_items(item_text_handler.encountered)

def update_weapon_songs(mhdata):
    # unfortunately, song data linking is unknown, but we have a few pieces
    # We know where the text file is, and we know of the id -> notes linking.
    
    print("Beginning load of hunting horn melodies")
    print("Warning: Hunting Horn format is unknown, but we do have a few pieces...")
    print("We know where the text data, and we know the id -> notes file formats")
    print("Everything else has to be manually connected.")
    song_data = load_schema(msk.Msk, 'hm/wp/wp05/music_skill.msk')
    song_text_data = load_text("common/text/vfont/music_skill")

    # Mapping from english name -> a name dict
    melody_names_map = {v['en']:v for v in song_text_data.values()}

    print("Writing artifact files for melody english text entries")
    artifacts.write_names_artifact("melody_strings_en.txt", melody_names_map.keys())

    # adding NA to melody_names_map
    melody_names_map['N/A'] = { lang:'N/A' for lang in cfg.all_languages }

    # Create melody id -> all possible songs that apply that melody
    melody_note_artifacts = []
    melody_to_notes = {}
    for song_entry in song_data:
        notes = ''
        for i in range(4):
            note_idx = getattr(song_entry, f'note{i+1}')
            if note_idx < len(note_colors): # technically int max means note does not exist
                notes += note_colors[note_idx]

        # write a note of id -> notes for the artifacts 
        melody_note_artifacts.append(f'{song_entry.id},{notes}')
        melody_to_notes.setdefault(song_entry.id, [])
        melody_to_notes[song_entry.id].append(notes)

    print("Writing artifact files for id -> notes")
    artifacts.write_lines_artifact("melody_notes.txt", melody_note_artifacts)

    print("Merging text values and notes into weapon melodies")
    fields = ['name', 'effect1', 'effect2']
    for melody in mhdata.weapon_melodies.values():
        for field in fields:
            val_en = melody[field]['en']
            if val_en not in melody_names_map:
                print(f"Could not find GMD text entry for {val_en}")
                continue
            melody[field] = melody_names_map[val_en]

        if melody.id in melody_to_notes:
            melody['notes'] = [{'notes': notes} for notes in melody_to_notes[melody.id]]
        else:
            print("Could not find binary music notes entries for " + melody['name']['en'])

    # Write new data
    writer = create_writer()

    writer.save_base_map_csv(
        "weapons/weapon_melody_base.csv",
        mhdata.weapon_melodies,
        schema=schema.WeaponMelodyBaseSchema()
    )

    writer.save_data_csv(
        "weapons/weapon_melody_notes.csv",
        mhdata.weapon_melodies,
        key='notes'
    )

    print("Weapon Melody files updated\n")