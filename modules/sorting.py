import string


def seperate_alphabetically(objects, key=None):
    if key is None:
        key = lambda val: val

    separated = {}

    for obj in objects:

        val = key(obj)

        if type(val) != str:
            continue
        if len(val) <= 0:
            continue
        if val[0].lower() in string.ascii_lowercase:
            k = val[0].upper()
        else:
            k = '#'

        if k not in separated.keys():
            separated[k] = []

        separated[k].append(obj)

    return separated
