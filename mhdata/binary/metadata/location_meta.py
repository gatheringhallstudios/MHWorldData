from os.path import dirname, abspath
from mhdata.io.csv import read_csv

def load_area_map():
    this_dir = dirname(abspath(__file__))
    area_map = {int(r['id'], 16):r['name'] for r in read_csv(this_dir + '/metadata_files/area_map.csv')}
    return area_map
