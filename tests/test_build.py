import os
import os.path

from mhdata import build

def test_validates():
    assert build.validate(), "Validation should have succeeded"

def test_builds_sql(tmpdir):
    "Integration test to ensure the database builds"

    fname = tmpdir.join('tmpdb.sql')
    print(fname)
    build.build_sql_database(fname)

    dbexists = os.path.exists(fname)
    assert dbexists, 'Database should have been created'
