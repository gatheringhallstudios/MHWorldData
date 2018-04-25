import click
import sys

import mhwdata.load as data

from mhwdata.io import DataReaderWriter

# Python 3.6 dictionaries preserve insertion order, and python 3.7 added it to the spec officially
# Older versions of python won't maintain order when importing data for the build.
if sys.version_info < (3,6):
    print(f"WARNING: You are running python version {sys.version}, " +
        "but this application was designed for Python 3.6 and newer. ")
    print("Earlier versions of Python will still build the project, but will not have a consistent build.")
    print("When creating a final build, make sure to use a newer version of python.")

def make_writer():
    return DataReaderWriter(
        languages=data.supported_languages, 
        data_path='source_data/')

@click.group()
def repair():
    "Contains subcommands to repair (aka reorder) certain data elements"
    pass

@repair.command()
def rewards():
    "Reorders hunting rewards to match the condition order"
    
    writer = make_writer()

    for monster_id, monster_entry in data.monster_map.items():
        # If there are no rewards, skip
        if 'rewards' not in monster_entry:
            continue

        # This monster has no rewards...delete
        if not monster_entry['rewards']:
            del monster_entry['rewards']
            continue

        old_rewards = monster_entry['rewards']

        # Store all conditions here. Any still here at the end print a warning
        all_conditions = set(old_rewards.keys())

        # add all results to this phase here
        new_rewards = {}

        # now iterate on the conditions map. We're trying to match the order
        for condition_en in data.monster_reward_conditions_map.names('en'):
            if condition_en not in old_rewards.keys():
                continue
            new_rewards[condition_en] = old_rewards[condition_en]
            all_conditions.remove(condition_en)

        # Now add up all missing entries and show warnings
        for condition_en in all_conditions:
            new_rewards[condition_en] = old_rewards[condition_en]
            print(f"WARNING: {condition_en} in monster {monster_entry.name('en')} is an invalid entry")

        monster_entry['rewards'] = new_rewards

    # Now save the output. The actual monsters will be reordered by this operation
    writer.save_data_map('monsters/monster_rewards.json', data.monster_map, fields=['rewards'])
    print("Repair complete")

if __name__ == '__main__':
    repair()