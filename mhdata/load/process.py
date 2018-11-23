"""
Additional import step processes isolated to a separate file.
"""

from mhdata.io import DataMap
from decimal import *

def extend_decoration_chances(decoration_map: DataMap):
    """Calculates the drop tables given the decoration map.

    Each decoration is part of a drop table (decided by rarity), and feystones
    will individually land on a drop table. Once on a drop table, each decoration in that drop table
    has an "equal" chance within that drop table.

    Odds are listed here, with one typo (gleaming is actually glowing).
    https://docs.google.com/spreadsheets/d/1ysj6c2boC6GarFvMah34e6VviZeaoKB6QWovWLSGlsY/htmlview?usp=sharing&sle=true#
    """

    rarity_to_table = {
        5: 'C',
        6: 'B',
        7: 'A',
        8: 'S'
    }

    jewel_to_table_odds = {
        'mysterious': { 'C': 0.85, 'B': 0.15, 'A': 0,    'S': 0 },
        'glowing':    { 'C': 0.65, 'B': 0.34, 'A': 0.01, 'S': 0 },
        'worn':       { 'C': 0.10, 'B': 0.82, 'A': 0.06, 'S': 0.02 },
        'warped':     { 'C': 0,    'B': 0.77, 'A': 0.18, 'S': 0.05 },
    }

    drop_tables = rarity_to_table.values()
    
    # Calculate how many entries there are per drop table type
    table_counts = { table:0 for table in drop_tables }
    for entry in decoration_map.values():
        table = rarity_to_table[entry['rarity']]
        table_counts[table] += 1

    

    # Create an odds map for each drop table level
    # This maps type -> feystone -> probability
    odds_map = { }
    for table in drop_tables:
        odds_map[table] = {}
        for feystone, feystone_odds in jewel_to_table_odds.items():
            value = Decimal(feystone_odds[table]) / Decimal(table_counts[table])
            odds_map[table][feystone] = value.quantize(Decimal('1.00000'))

    # Assign the odds map for the drop table level to the decoration itself
    
    for entry in decoration_map.values():
        table = rarity_to_table[entry['rarity']]
        entry['chances'] = odds_map[table]
