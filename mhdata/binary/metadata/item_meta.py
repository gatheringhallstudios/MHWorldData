from os.path import dirname, abspath, join

class ItemMeta:
    def __init__(self):
        this_dir = dirname(abspath(__file__))

        # load kulve weapons
        kulve_file = open(this_dir + '/metadata_files/kulve_weapons.txt', encoding="utf8")
        self.kulve_weapons = set(line.strip() for line in kulve_file.readlines())