from typing import List

from bitnest.core import Expression, Symbol


def _inspect_datatype(datatype: Expression):
    fields = []
    depth = 0
    regions = {}

    def replacement_function(symbol, args):
        nonlocal fields
        nonlocal depth
        nonlocal regions

        if symbol == Symbol("field"):
            symbol, args = yield (symbol, *args)
            fields.append((symbol, *args))
            yield (symbol, *args)
        elif symbol == Symbol("vector"):
            depth = depth + 1
            start = len(fields)
            symbol, args = yield (symbol, *args)
            depth = depth - 1
            regions[(depth, start, len(fields))] = (symbol, *args)
            yield (symbol, *args)
        elif symbol == Symbol("struct"):
            depth = depth + 1
            start = len(fields)
            symbol, args = yield (symbol, *args)
            depth = depth - 1
            regions[(depth, start, len(fields))] = (symbol, *args)
            yield (symbol, *args)
        else:
            symbol, args = yield (symbol, *args)
            yield (symbol, *args)

    datatype.replace(replacement_function=replacement_function)
    return (datatype, fields, regions)


def inspect_datatypes(path: Expression) -> List:
    _path = Expression(path)

    datatypes = _path.find_symbol(Symbol("datatype"))
    datatype_regions = []

    for datatype in datatypes:
        datatype_regions.append(_inspect_datatype(datatype))
    return datatype_regions
