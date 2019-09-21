from typing import Type, Mapping
import re
from os.path import dirname, abspath, join

from mhw_armor_edit import ftypes
from mhw_armor_edit.ftypes import gmd

# Location of MHW binary data.
# Looks for a folder called /mergedchunks neighboring the main project folder.
# This folder should be created via WorldChunkTool, with each numbered chunk being
# moved into the mergedchunks folder in ascending order (with overwrite).
CHUNK_DIRECTORY = join(dirname(abspath(__file__)), "../../../../../mergedchunks")

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

def get_chunk_root():
    return CHUNK_DIRECTORY

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