import os.path

supported_languages = None

def set_languages(languages):
    "Sets the list of supported languages"
    global supported_languages
    supported_languages = languages

def get_languages():
    if not supported_languages:
        raise Exception("Supported Languages not set, use the set_languages function")
    return supported_languages

def get_data_path(file_in_data_folder):
    "Returns a file path to something stored in the data folder. Used internally"
    this_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(this_dir, '../../data/', file_in_data_folder)
    return os.path.normpath(data_dir)
