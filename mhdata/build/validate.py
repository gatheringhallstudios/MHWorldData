import itertools

from mhdata.io import DataMap
from mhdata.util import ensure_warn

import mhdata.load.cfg as cfg

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
    errors.extend(validate_armor(mhdata))

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
    uncapped_conditions = ("Quest Reward / Investigation (Bronze)")

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

def validate_armor(mhdata):
    errors = []

    # Checks if any pieces of armor is listed in two different sets
    encountered_armors = set()

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

    return errors