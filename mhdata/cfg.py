"""
Contains configuration data for interacting with the source_data folder.
These are hardcoded here as this is meant to be a dumping 
ground. Source_data is not actually user configurable.

For customized data loading, use mhwdata.io directly.
"""

supported_ranks = ('LR', 'HR')

"A mapping of all translations"
all_languages = {
    'en': "English",
    'ja': "日本語",
    'fr': 'Français',
    'it': 'Italiano',
    'de': 'Deutsch',
    'es': 'Español',
    'pt': 'Português do Brasil',
    'pl': 'Polski',
    'ru': 'Pусский',
    'ko': '한국어',
    'zh': '繁體中文',
    'ar': 'Arabe'
}

"A list of languages that require complete translations. Used in validation"
required_languages = ('en',)

"A list of languages that can be exported"
supported_languages = ('en', 'ja')

"Languages that are designated as potentially incomplete"
incomplete_languages = ('ja',)

"List of all possible armor parts"
armor_parts = ('head', 'chest', 'arms', 'waist', 'legs')

"Maximum number of items in a recipe"
max_recipe_item_count = 4

"Maximum number of skills in an armor piece/weapon"
max_skill_count = 2

GREAT_SWORD = 'great-sword'
LONG_SWORD = 'long-sword'
SWORD_AND_SHEILD = 'sword-and-shield'
DUAL_BLADES = 'dual-blades'
HAMMER = 'hammer'
HUNTING_HORN = 'hunting-horn'
LANCE = 'lance'
GUNLANCE = 'gunlance'
SWITCH_AXE = 'switch-axe'
CHARGE_BLADE = 'charge-blade'
INSECT_GLAIVE = 'insect-glaive'
LIGHT_BOWGUN = 'light-bowgun'
HEAVY_BOWGUN = 'heavy-bowgun'
BOW = 'bow'

"A list of all melee weapon types"
weapon_types_melee = (GREAT_SWORD, LONG_SWORD, SWORD_AND_SHEILD, DUAL_BLADES,
    HAMMER, HUNTING_HORN, LANCE, GUNLANCE, SWITCH_AXE, CHARGE_BLADE,
    INSECT_GLAIVE)

"A list of all bowgun weapon types"
weapon_types_gun = (LIGHT_BOWGUN, HEAVY_BOWGUN)

"A list of all ranged weapon types"
weapon_types_ranged = (*weapon_types_gun, BOW)

"A list of all weapon types"
weapon_types = (*weapon_types_melee, *weapon_types_ranged)

"Valid possible kinsect boosts"
valid_kinsects = ('sever', 'blunt', 'speed', 'element', 'health', 'stamina')

"Valid possible phial types (switchaxe and chargeblade)"
valid_phials = ('power', 'power element', 'dragon', 'poison', 'paralysis', 'exhaust', 'impact')

"Valid gunlance shelling types"
valid_shellings = ('normal', 'wide', 'long')

# notes are (white, purple, red, cyan, blue, green, orange, yellow)
"Valid notes for hunting horns"
valid_notes = ('W', 'P', 'R', 'C', 'B', 'G', 'O', 'Y')

icon_colors = [
    "Gray", "White", "Lime", "Green", "Cyan", "Blue", "Violet", "Orange",
    "Pink", "Red", "DarkRed", "LightBeige", "Beige", "DarkBeige", "Yellow",
    "Gold", "DarkGreen", "DarkPurple"
]