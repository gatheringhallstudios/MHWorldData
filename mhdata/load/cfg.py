"""
Contains configuration data for interacting with the source_data folder.
These are hardcoded here as this is meant to be a dumping 
ground. Source_data is not actually user configurable.

For configurable data loading, use mhwdata.io directly.
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
