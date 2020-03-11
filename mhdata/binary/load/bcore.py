"""
Miscellanious loading functions that form the backbone of binary loading.
Consider whether this should be part of parsers, or if its fine to have here.
"""

from typing import Type, Mapping, MutableMapping, Union
import regex as re
from os.path import dirname, abspath, join

from mhw_armor_edit import ftypes
from mhw_armor_edit.ftypes import gmd

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
    'ita': 'it',
    'ger': 'de',
    'spa': 'es',
    'ptB': 'pt',
    'pol': 'pl',
    'rus': 'ru',
    'kor': 'ko',
    'chT': 'zh',
    'ara': 'ar',
}

def get_chunk_root():
    return CHUNK_DIRECTORY

def load_schema(schema: Type[ftypes.StructFile], relative_dir: str) -> ftypes.StructFile:
    "Uses an ftypes struct file class to load() a file relative to the chunk directory"
    with open(join(CHUNK_DIRECTORY, relative_dir), 'rb') as f:
        return schema.load(f)

class GmdGroup(Mapping[Union[int, str], Mapping[str,str]]):
    def __init__(self, indexed_entries, keyed_entries):
        self.indexed_entries = indexed_entries
        self.keyed_entries = keyed_entries

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.indexed_entries[key]
        else:
            return self.keyed_entries[str(key)]

    def __len__(self):
        return len(self.indexed_entries) + len(self.keyed_entries)

    def __iter__(self):
        yield from self.indexed_entries
        yield from self.keyed_entries

def load_text(basepath: str, exclude_indices=False, exclude_keys=False) -> GmdGroup:
    """Parses a series of GMD files, returning a mapping from index -> language -> value
    
    The given base path is the relative directory from the chunk folder,
    excluding the _eng.gmd ending. All GMD files starting with the given basepath
    and ending with the language are combined together into a single result.
    """
    indexed_entries = {}
    keyed_entries = {}
    for ext_lang, lang in lang_map.items():
        data = load_schema(gmd.Gmd, f"{basepath}_{ext_lang}.gmd")
        for idx, value_obj in enumerate(data.items):
            if idx not in indexed_entries and not exclude_indices:
                indexed_entries[idx] = {}
            if value_obj.key not in keyed_entries and not exclude_keys:
                keyed_entries[value_obj.key] = {}

            value = value_obj.value

            # For german, treat - as a linebreak join if between lowercase characters
            if lang == 'de':
                value = re.sub(r"(\p{Ll})-( )*\r?\n( )*(\p{Ll})", r"\1\4", value)

            value = re.sub(r"-()*\r?\n( )*", "-", value)
            value = re.sub(r"( )*\r?\n( )*", " ", value)
            value = re.sub(r"( )?<ICON ALPHA>", " α", value)
            value = re.sub(r"( )?<ICON BETA>", " β", value)
            value = re.sub(r"( )?<ICON GAMMA>", " γ", value)
            value = (value
                .replace("<STYL MOJI_YELLOW_DEFAULT>[1]</STYL>", "[1]")
                .replace("<STYL MOJI_YELLOW_DEFAULT>[2]</STYL>", "[2]")
                .replace("<STYL MOJI_YELLOW_DEFAULT>[3]</STYL>", "[3]")
                .replace("<STYL MOJI_YELLOW_DEFAULT>", "")
                .replace("<STYL MOJI_LIGHTBLUE_DEFAULT>", "")
                .replace("</STYL>", "")).strip()

            if not exclude_indices: indexed_entries[idx][lang] = value
            if not exclude_keys: keyed_entries[value_obj.key][lang] = value

    return GmdGroup(indexed_entries, keyed_entries)
