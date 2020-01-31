"""
Additional import step processes isolated to a separate file.
"""

from mhdata.io import DataMap, data_path
from mhdata.io.csv import read_csv
from decimal import *

from os.path import join

from mhdata import cfg

def copy_skill_descriptions(skill_map: DataMap):
    """Copies the descriptions of certain skill levels to the skill tree.

    Some skill trees are "artificial" and do not exist in the game, therefore they
    have no actual description. This includes skills like Good Luck. Therefore,
    should certain conditions be applied, we reuse the skill detail description.

    The conditions for it to occur are:
    - Missing an english description (missing a translation shouldn't trigger this)
    - Only one available skill level (multi-stage skills are ignored)
    """

    for tree_entry in skill_map.values():
        if tree_entry['description']['en']:
            continue
        if len(tree_entry['levels']) != 1:
            continue
        
        # We don't do a default translation here, since its handled by another part of the build
        level_entry = tree_entry['levels'][0]
        for language in cfg.supported_languages:
            tree_entry['description'][language] = level_entry['description'][language]

def extend_decoration_chances(decoration_map: DataMap):
    """Calculates the drop tables given the decoration map.

    Each decoration is part of a drop table (decided by rarity), and feystones
    will individually land on a drop table. Once on a drop table, each decoration in that drop table
    has an "equal" chance within that drop table.

    Odds are listed here, with one typo (gleaming is actually glowing).
    https://docs.google.com/spreadsheets/d/1ysj6c2boC6GarFvMah34e6VviZeaoKB6QWovWLSGlsY/htmlview?usp=sharing&sle=true#
    """

    jewel_to_table_odds = {}
    droprates = read_csv(join(data_path, "decorations/decoration_droprates.csv"))
    for row in droprates:
        entries = {}
        for i in range(5, 14):
            entries[i] = int(row[str(i)] or '0')
        jewel_to_table_odds[row['feystone']] = entries
    
    # Calculate how many entries there are per drop table type
    table_counts = { table:0 for table in range(5, 14) }
    for entry in decoration_map.values():
        table_counts[entry['rarity']] += 1

    # Create an odds map for each drop table level
    # This maps droptable -> feystone -> probability
    # This is necessary because all decorations are assigned to a droptable
    odds_map = { }
    for table in range(5, 14):
        odds_map[table] = {}
        for feystone, feystone_odds in jewel_to_table_odds.items():
            count = table_counts[table]
            if count == 0:
                continue
            value = Decimal(feystone_odds[table]) / Decimal(count)
            odds_map[table][feystone] = value.quantize(Decimal('1.00000'))

    # Assign the odds map for the drop table level to the decoration itself
    for entry in decoration_map.values():
        entry['chances'] = odds_map[entry['rarity']]
