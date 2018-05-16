import os
import os.path
import pytest

from mhdata import build
from mhdata.load import load_data

@pytest.fixture()
def mhdata():
    return load_data()

def test_validates(mhdata):
    assert build.validate(mhdata), "Validation should have succeeded"

def test_builds_sql(tmpdir, mhdata):
    "Integration test to ensure the database builds"

    fname = tmpdir.join('tmpdb.sql')
    print(fname)
    build.build_sql_database(fname, mhdata)

    dbexists = os.path.exists(fname)
    assert dbexists, 'Database should have been created'
