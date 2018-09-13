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
    'ja': "Japanese"
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

"A list of all melee weapon types"
weapon_types_melee = ('great-sword', 'long-sword', 'sword-and-shield', 'dual-blades',
    'hammer', 'hunting-horn', 'lance', 'gunlance', 'switch-axe', 'charge-blade',
    'insect-glaive')

weapon_types_bow = 'bow'

weapon_types_gun = ('light-bowgun', 'heavy-bowgun')

"A list of all ranged weapon types"
weapon_types_ranged = (*weapon_types_gun, weapon_types_bow)

"A list of all weapon types"
weapon_types = (*weapon_types_melee, *weapon_types_ranged)

"Valid possible kinsect boosts"
valid_kinsects = ('sever', 'blunt', 'speed', 'element', 'health', 'stamina')

"Valid possible phial types (switchaxe and chargeblade)"
valid_phials = ('power', 'power element', 'dragon', 'poison', 'paralysis', 'exhaust', 'impact')

"Valid gunlance shelling types"
valid_shellings = ('normal', 'wide', 'long')

icon_colors = [
    "Gray", "White", "Lime", "Green", "Cyan", "Blue", "Violet", "Orange",
    "Pink", "Red", "DarkRed", "LightBeige", "Beige", "DarkBeige", "Yellow",
    "Gold", "DarkGreen", "DarkPurple"
]