import itertools

from mhdata import cfg
from mhdata.io import DataMap
from mhdata.util import ensure_warn

from . import datafn

supported_languages = cfg.supported_languages
all_languages = cfg.all_languages
incomplete_languages = cfg.incomplete_languages
supported_ranks = cfg.supported_ranks

def validate(mhdata):
    "Perform all validations, print out the errors, and return if it succeeded or not"
    errors = []
    errors.extend(validate_items(mhdata))
    errors.extend(validate_locations(mhdata))
    errors.extend(validate_monsters(mhdata))
    errors.extend(validate_monster_rewards(mhdata))
    errors.extend(validate_skills(mhdata))
    errors.extend(validate_armor(mhdata))
    errors.extend(validate_weapons(mhdata))
    errors.extend(validate_charms(mhdata))

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return False

    return True


def validate_items(mhdata):
    errors = []

    # check for existance in item combinations
    for combo in mhdata.item_combinations:
        items = (combo['result'], combo['first'], combo['second'])
        items = filter(None, items)  # removes nulls
        for item in items:
            if item not in mhdata.item_map.names('en'):
                errors.append(f"{item} in combinations doesn't exist")

    return errors


def validate_locations(mhdata):
    errors = []

    for location_entry in mhdata.location_map.values():
        for item_entry in location_entry['items']:
            item_lang = item_entry['item_lang']
            item_name = item_entry['item']
            if item_name not in mhdata.item_map.names(item_lang):
                errors.append(f"{item_name} in location items doesn't exist")

    return errors


def validate_monsters(mhdata):
    errors = []

    # Check that all monsters have hitzones
    for entry in mhdata.monster_map.values():
        ensure_warn('hitzones' in entry, f"Monster {entry.name('en')} missing hitzones")
    
    # Check that large monsters have weakness and normal is included
    for entry in mhdata.monster_map.values():
        if entry['size'] == 'small':
            continue

        name = entry.name('en')

        if 'weaknesses' not in entry:
            print(f"Warning: Large monster {name} does not contain a weakness entry")
            continue

        if 'normal' not in entry['weaknesses']:
            errors.append(f"Invalid weaknesses in {name}, normal is a required state")

    return errors


def validate_monster_rewards(mhdata):
    """Validates monster rewards for sane values. 
    Certain fields (like carve) sum to 100, 
    Others (like quest rewards) must be at least 100%"""

    # Those other than these are validated for 100% drop rate EXACT.
    # Quest rewards sometimes contain a guaranteed reward.
    # We should probably separate, but most databases don't separate them.
    # Investigate further
    uncapped_conditions = ("Quest Reward (Bronze)")

    errors = set()
    
    for monster_id, entry in mhdata.monster_map.items():
        if 'rewards' not in entry:
            continue

        monster_name = entry.name('en') # used for error display

        # accumulates percentages by rank
        reward_percentages = { rank:[] for rank in supported_ranks }

        valid = True
        for reward in entry['rewards']:
            condition = reward['condition_en']
            rank = reward['rank']

            # ensure condition exists
            if condition not in mhdata.monster_reward_conditions_map.names('en'):
                errors.add(f"Invalid condition {condition} in monster {monster_name}")
                valid = False

            if reward['item_en'] not in mhdata.item_map.names('en'):
                errors.add(f"Monster reward item {reward['item_en']} doesn't exist")
                valid = False

            if rank not in supported_ranks:
                errors.add(f"Unsupported rank {rank} in {monster_name} rewards")
                valid = False

        if not valid:
            continue
        
        # Ensure percentage is correct (at or greater than 100)
        rank_reward_key_fn = lambda r: (r['rank'], r['condition_en'])
        sorted_rewards = sorted(entry['rewards'], key=rank_reward_key_fn)
        for (rank, condition), items in itertools.groupby(sorted_rewards, rank_reward_key_fn):
            percentage_sum = sum((int(r['percentage']) for r in items), 0)

            key_str = f"(rank {rank} condition {condition})"
            error_start = f"Rewards %'s for monster {monster_name} {key_str}"
            if condition not in uncapped_conditions:
                ensure_warn(
                    percentage_sum == 100, 
                    f"{error_start} does not sum to 100")
            else:
                ensure_warn(
                    percentage_sum >= 100, 
                    f"{error_start} does not sum to at least 100")

    return errors


def validate_skills(mhdata):
    errors = []

    for skill in mhdata.skill_map.values():
        skill_name = skill['name']['en']
        expected_max = len(skill['levels'])
        encountered_levels = set()
        for level in skill['levels']:
            level_value = level['level']
            if level_value < 0 or level_value > expected_max:
                errors.append(f"Skill {skill_name} has out of range effect {level_value}")
                continue
            encountered_levels.add(level_value)
        if len(encountered_levels) != expected_max:
            errors.append(f"Skill {skill_name} is missing effect levels")

    return errors


def validate_armor(mhdata):
    errors = []

    # Checks if any pieces of armor is listed in two different sets
    encountered_armors = set()

    # Validate armorsets
    for setentry in mhdata.armorset_map.values():
        setname = setentry.name('en')
        armor_lang = setentry['armor_lang']
        
        # All armor pieces in the set
        armor_names = [setentry[part] for part in cfg.armor_parts]
        armor_names = list(filter(None, armor_names))

        if not armor_names:
            print(f"Warning: {setname} has no armor entries")

        for armor_name in armor_names:
            armor_id = mhdata.armor_map.id_of(armor_lang, armor_name)
            
            if not armor_id:
                errors.append(f"{setname} has invalid armor {armor_name}")
                continue
            if armor_id in encountered_armors:
                errors.append(f"{setname} has duplicated armor {armor_name}")
                continue

            encountered_armors.add(armor_id)

    # Validate Armor
    for armor_entry in mhdata.armor_map.values():
        # Ensure that all armor items were encountered
        if armor_entry.id not in encountered_armors:
            errors.append(f"Armor {armor_entry.name('en')} is not in an armor set")

        # Ensure items exist
        for item_name, _ in datafn.iter_armor_recipe(armor_entry):
            if item_name not in mhdata.item_map.names('en'):
                errors.append(f"Item {item_name} in armors does not exist")

        # Ensure skills exist
        for skill_name, _ in datafn.iter_skill_points(armor_entry):
            if skill_name not in mhdata.skill_map.names('en'):
                errors.append(f"Skill {skill_name} in armors does not exist")

    # Validate Armorset bonuses
    for bonus_entry in mhdata.armorset_bonus_map.values():
        for skill_name, _ in datafn.iter_setbonus_skills(bonus_entry):
            if skill_name not in mhdata.skill_map.names('en'):
                errors.append(f"Skill {skill_name} in set bonuses does not exist")

    return errors

def validate_weapons(mhdata):
    errors = []
    for entry in mhdata.weapon_map.values():
        weapon_type = entry['weapon_type']
        if weapon_type in cfg.weapon_types_melee and not entry.get('sharpness', None):
            errors.append(f"Melee weapon {entry.name('en')} does not have a sharpness value")
        if not entry.get('craft', {}):
            errors.append(f"Weapon {entry.name('en')} does not have any recipes")
        if weapon_type == cfg.weapon_types_bow and not entry.get('bow', None):
            errors.append(f"Weapon {entry.name('en')} is missing bow data")
        if weapon_type in cfg.weapon_types_gun:
            if not entry.get('ammo_config', None):
                errors.append(f"Weapon {entry.name('en')} is missing ammo config")
            elif entry['ammo_config'] not in mhdata.weapon_ammo_map:
                errors.append(f"Weapon {entry.name('en')} has invalid ammo config")

    return errors

def validate_charms(mhdata):
    errors = []

    names = mhdata.charm_map.names("en")
    for entry in mhdata.charm_map.values():
        previous_entry = entry['previous_en']
        if previous_entry is not None and previous_entry not in names:
            errors.append(f"Charm {previous_entry} for previous_en does not exist")

    return errors