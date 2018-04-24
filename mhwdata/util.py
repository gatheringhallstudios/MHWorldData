def ensure(field, error_message):
    "Tests that the field is truthy, throwing an Exception if its not"
    if not field:
        raise Exception("ERROR: " + error_message)

def ensure_warn(field, error_message):
    "Tests that the field is truthy, printing a warning message if its not"
    if not field:
        print("WARNING: " + error_message)

def get_duplicates(iterable):
    "Checks the iterable for duplicate entries, and returns them"
    seen = set()
    duplicates = []
    for item in iterable:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)

    return duplicates
