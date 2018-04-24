import os
import os.path

from mhwdata import build

def test_builds(tmpdir):
    "Integration test to ensure the database builds"

    fname = tmpdir.join('tmpdb.sql')
    print(fname)
    build.build_database(fname)

    dbexists = os.path.exists(fname)
    assert dbexists, 'Database should have been created'
