"""Transformation to realize a given struct into all possible
datatypes and uniquely label all fields

"""
import itertools

from bitnest.core import Expression, Symbol, list_


def realize_datatypes(struct: Expression) -> Expression:
    _struct = Expression(struct)
    counter = itertools.count()

    def handle_field(symbol, args):
        field_type, name, offset, size, id, additional = args
        return [(symbol, field_type, name, offset, size, next(counter), additional)]

    def handle_vector(symbol, args):
        paths = []
        struct_paths, length, loop_variable = args
        for struct in struct_paths:
            paths.append((symbol, struct, length, loop_variable))
        return paths

    def handle_union(symbol, args):
        paths = []
        for struct_paths in args:
            for struct in struct_paths:
                paths.append(struct)
        return paths

    def handle_struct(symbol, args):
        name, fields, conditions, additional = args
        paths = []
        for _fields in itertools.product(*fields[1:]):
            paths.append(
                (symbol, name, (Symbol("list"), *_fields), conditions, additional)
            )
        return paths

    replacement_mapping = {
        Symbol("field"): handle_field,
        Symbol("vector"): handle_vector,
        Symbol("union"): handle_union,
        Symbol("struct"): handle_struct,
    }

    _struct.replace(replacement_mapping, order="post_order")
    return list_(*[(Symbol("datatype"), _) for _ in _struct.expression])
