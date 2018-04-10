import pytest

# todo: refactor fixture usage to automatically create files and allow parallel execution

@pytest.fixture(scope="module")
def basedata():
    return [
        {
            'name': { 'en': 'test1', 'ja': 'test1j' }
        },
        {
            'name': { 'en': 'test2', 'ja': 'test2j' }
        },
        {
            'name': { 'en': 'test3', 'ja': 'test3j' }
        }
    ]

@pytest.fixture(scope="module")
def subdata(basedata):
    test_data = {}
    for item in basedata:
        test_data[item['name']['en']] = { 'data': item['name']['en'] }
    return test_data