"""
Transformation to add field offsets within a given datatype

"""
from bitnest.core import Expression, Integer, Symbol


def realize_offsets(path: Expression) -> Expression:
    _path = Expression(path)

    current_offset = None

    def replacement_function(symbol, args):
        nonlocal current_offset

        if symbol == Symbol("datatype"):
            current_offset = Integer(0)
            symbol, args = yield (symbol, *args)
            current_offset = None
            yield (symbol, *args)
        elif symbol == Symbol("field"):
            field_type, name, offset, size, additional = args
            field = (
                symbol,
                field_type,
                name,
                current_offset.expression,
                size,
                additional,
            )
            current_offset = current_offset + size
            symbol, args = yield field
            yield (symbol, *args)
        elif symbol == Symbol("vector"):
            struct, length, loop_variable = args
            current_offset = current_offset + (
                Expression(length) * Expression(loop_variable)
            )
            symbol, args = yield (symbol, *args)
            yield (symbol, *args)
        else:
            symbol, args = yield (symbol, *args)
            yield (symbol, *args)

    _path.replace(replacement_function=replacement_function)
    return _path
