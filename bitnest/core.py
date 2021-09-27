import itertools

from bitnest.ast.core import Symbol, Expression


def realize_datatype_paths(struct):
    if not isinstance(struct, Expression):
        struct = Expression(struct)

    def handle_field(symbol, args):
        field_type, name, offset, size, additional = args
        return [(symbol, *args)]

    def handle_vector(symbol, args):
        paths = []
        struct_paths, length = args
        for struct in struct_paths:
            paths.append((symbol, struct, length))
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
            paths.append((symbol, name, (Symbol('list'), *_fields), conditions, additional))
        return paths

    replacement_mapping = {
        Symbol('field'): handle_field,
        Symbol('vector'): handle_vector,
        Symbol('union'): handle_union,
        Symbol('struct'): handle_struct,
    }

    struct.replace(replacement_mapping, order='post_order')
    return struct.expression


# def _get_path_fields(path, fields, structs, depth=0):
#     start = len(fields)
#     if isinstance(path, Field):
#         fields.append(path)
#     elif isinstance(path, tuple):
#         if issubclass(path[0], Struct):
#             for element in path[1:]:
#                 _get_path_fields(element, fields, structs, depth=depth + 1)
#             structs[(depth, start, len(fields))] = path[0]
#         elif issubclass(path[0], Vector):
#             _get_path_fields(path[1], fields, structs, depth=depth + 1)
#             structs[(depth, start, len(fields))] = path[0]


# def get_path_fields(path):
#     fields = []
#     structs = {}
#     _get_path_fields(path, fields, structs)
#     return fields, structs


# def _realize_conditions(struct):
#     conditions = []

#     for _condition in struct.conditions:
#         conditions.append((struct, _condition))

#     for field in struct.fields:
#         if isinstance(field, Union):
#             for union_struct in field.structs:
#                 _conditions = _realize_conditions(union_struct)
#                 for _struct, _condition in _conditions:
#                     conditions.append(
#                         (
#                             (field.__class__, union_struct, _struct),
#                             (field.__class__, union_struct, _condition),
#                         )
#                     )
#         elif isinstance(field, Vector):
#             _conditions = _realize_conditions(field.klass)
#             for _struct, _condition in _conditions:
#                 conditions.append(
#                     (
#                         (field.__class__, field.klass, _struct),
#                         (field.__class__, field.klass, _condition),
#                     )
#                 )
#         elif isinstance(field, Field):
#             pass
#         elif issubclass(field, Struct):
#             _conditions = _realize_conditions(field)
#             for _struct, _condition in _conditions:
#                 conditions.append(((struct, _struct), (struct, _condition)))

#     return conditions


# def realize_conditions(root_class):
#     return _realize_conditions(root_class)


# def format_tuple(t):
#     def _format_tuple(t):
#         if isinstance(t, type):
#             return t.__name__
#         elif isinstance(t, tuple):
#             return tuple(_format_tuple(_) for _ in t)
#         else:
#             return t

#     return _format_tuple(t)
