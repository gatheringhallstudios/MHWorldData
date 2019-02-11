import os
import os.path
import pytest

from mhdata import build
from mhdata.load import load_data, load_data_processed, validate

@pytest.fixture()
def mhdata_raw():
    return load_data()

@pytest.fixture()
def mhdata():
    return load_data_processed()

def test_validates(mhdata_raw):
    assert validate(mhdata_raw), "Validation should have succeeded"

def test_builds_sql(tmpdir, mhdata):
    "Integration test to ensure the database builds"

    fname = tmpdir.join('tmpdb.sql')
    print(fname)
    build.build_sql_database(fname, mhdata)

    dbexists = os.path.exists(fname)
    assert dbexists, 'Database should have been created'
