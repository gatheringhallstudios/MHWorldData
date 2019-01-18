from typing import Type, Mapping, Iterable
from os.path import dirname, abspath, join
import re

from mhdata.util import OrderedSet, Sharpness

from mhw_armor_edit import ftypes
from mhw_armor_edit.ftypes import gmd, kire, wp_dat

# Location of MHW binary data.
# Looks for a folder called /mergedchunks neighboring the main project folder.
# This folder should be created via WorldChunkTool, with each numbered chunk being
# moved into the mergedchunks folder in ascending order (with overwrite).
CHUNK_DIRECTORY = join(dirname(abspath(__file__)), "../../../../mergedchunks")

# Mapping from GMD filename suffix to actual language code
lang_map = {
    'eng': 'en',
    'jpn': 'ja',
    'fre': 'fr',
    'ger': 'de',
    'ita': 'it',
    'spa': 'es',
    'ptB': 'pt',
    'pol': 'pl',
    'rus': 'ru',
    'kor': 'ko',
    'chT': 'zh',
    'ara': 'ar',
}

def load_schema(schema: Type[ftypes.StructFile], relative_dir: str) -> ftypes.StructFile:
    "Uses an ftypes struct file class to load() a file relative to the chunk directory"
    with open(join(CHUNK_DIRECTORY, relative_dir), 'rb') as f:
        return schema.load(f)

def load_text(basepath: str) -> Mapping[int, Mapping[str, str]]:
    """Parses a series of GMD files, returning a mapping from index -> language -> value
    
    The given base path is the relative directory from the chunk folder,
    excluding the _eng.gmd ending. All GMD files starting with the given basepath
    and ending with the language are combined together into a single result.
    """
    results = {}
    for ext_lang, lang in lang_map.items():
        data = load_schema(gmd.Gmd, f"{basepath}_{ext_lang}.gmd")
        for idx, value_obj in enumerate(data.items):
            if idx not in results:
                results[idx] = {}
            value = value_obj.value
            value = re.sub(r"( )*\r?\n( )*", " ", value)
            value = re.sub(r"( )?<ICON ALPHA>", " α", value)
            value = re.sub(r"( )?<ICON BETA>", " β", value)
            value = re.sub(r"( )?<ICON GAMMA>", " γ", value)
            results[idx][lang] = (value
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[1]</STYL>", "[1]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[2]</STYL>", "[2]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>[3]</STYL>", "[3]")
                                    .replace("<STYL MOJI_YELLOW_DEFAULT>", "")
                                    .replace("<STYL MOJI_LIGHTBLUE_DEFAULT>", "")
                                    .replace("</STYL>", "")).strip()
    return results

class ItemTextHandler():
    "A class that loads item text and tracks encountered items"

    def __init__(self):
        self._item_text = load_text("common/text/steam/item")
        self.encountered = OrderedSet()

    def name_for(self, item_id: int):
        self.encountered.add(item_id)
        return self._item_text[item_id * 2]

    def description_for(self, item_id: int):
        self.encountered.add(item_id)
        return self._item_text[item_id * 2 + 1]

    def text_for(self, item_id: int):
        self.encountered.add(item_id)
        return (self._item_text[item_id * 2], self._item_text[item_id * 2 + 1])

class SharpnessDataReader():
    "A class that loads sharpness data and processes it for binary weapon objects"
    def __init__(self):
        self.sharpness_data = load_schema(kire.Kire, "common/equip/kireaji.kire")

    def sharpness_for(self, binary: wp_dat.WpDatEntry):
        """"Returns sharpness data for the given binary weapon entry.
        This sharpness data is in the form used in the sharpness csv file"""

        sharpness_binary = self.sharpness_data[binary.kire_id]
        sharpness_modifier = -250 + (binary.handicraft*50)
        sharpness_maxed = sharpness_modifier == 0
        if not sharpness_maxed:
            sharpness_modifier += 50 # we store the handicraft+5 value...

        # Binary data lists "end" positions, not pool sizes
        # So we convert by subtracting the previous end position
        sharpness_values = Sharpness(
            red=sharpness_binary.red,
            orange=sharpness_binary.orange-sharpness_binary.red,
            yellow=sharpness_binary.yellow-sharpness_binary.orange,
            green=sharpness_binary.green-sharpness_binary.yellow,
            blue=sharpness_binary.blue-sharpness_binary.green,
            white=sharpness_binary.white-sharpness_binary.blue,
            purple=sharpness_binary.purple-sharpness_binary.white)
        sharpness_values.subtract(-sharpness_modifier)

        return {
            'maxed': sharpness_maxed,
            **sharpness_values.to_object()
        }
        
def convert_recipe(item_text_handler: ItemTextHandler, recipe_binary) -> dict:
    "Converts a recipe binary (of type eq_cus/eq_crt) to a dictionary"
    new_data = {}
    
    for i in range(1, 4+1):
        item_id = getattr(recipe_binary, f'item{i}_id')
        item_qty = getattr(recipe_binary, f'item{i}_qty')

        item_name = None if item_qty == 0 else item_text_handler.name_for(item_id)['en']
        new_data[f'item{i}_name'] = item_name
        new_data[f'item{i}_qty'] = item_qty if item_qty else None

    return new_data