import itertools

from bitnest.field import Struct, Field, Union, Vector


def _realize_datatype(struct):
    datatype = [struct]

    for field in struct.fields:
        if isinstance(field, Union):
            union_datatype = [field.__class__]
            for union_struct in field.structs:
                _datatype = _realize_datatype(union_struct)
                union_datatype.append(_datatype)
            datatype.append(tuple(union_datatype))
        elif isinstance(field, Vector):
            _datatype = _realize_datatype(field.klass)
            datatype.append((field.__class__, _datatype))
        elif isinstance(field, Field):
            datatype.append(field)
        elif issubclass(field, Struct):
            _datatype = _realize_datatype(field)
            datatype.append(_datatype)
    return tuple(datatype)


def realize_datatype(struct):
    return _realize_datatype(struct)


def _realize_datatype_paths(datatype):
    if isinstance(datatype, tuple):
        if issubclass(datatype[0], Vector):
            # (Vector, Struct, ...) -> (Vector, paths(Struct, ...))
            field_paths = []
            _field_paths = _realize_datatype_paths(datatype[1])
            for field_path in _field_paths:
                field_paths.append((datatype[0], field_path))
            return field_paths
        elif issubclass(datatype[0], Union):
            # (Union, (Field, (Struct, ...), ...)) -> paths(Field) + paths(Union, ...) + ... + paths(...)
            union_paths = []
            for union_struct in datatype[1:]:
                for union_path in _realize_datatype_paths(union_struct):
                    union_paths.append(union_path)
            return union_paths
        elif issubclass(datatype[0], Struct):
            # (Struct, ...) -> product(paths(0), ..., paths(N))
            field_paths = []
            for element in datatype[1:]:
                field_paths.append(_realize_datatype_paths(element))

            _paths = []
            for path in itertools.product(*field_paths):
                _paths.append((datatype[0], *path))
            return _paths
    elif isinstance(datatype, Field):
        # Field -> ((Field))
        return (datatype,)


def realize_datatype_paths(datatype):
    return _realize_datatype_paths(datatype)


def _get_path_fields(path, fields, structs, depth=0):
    start = len(fields)
    if isinstance(path, Field):
        fields.append(path)
    elif isinstance(path, tuple):
        if issubclass(path[0], Struct):
            for element in path[1:]:
                _get_path_fields(element, fields, structs, depth=depth+1)
            structs[(depth, start, len(fields))] = path[0]
        elif issubclass(path[0], Vector):
            _get_path_fields(path[1], fields, structs, depth=depth+1)
            structs[(depth, start, len(fields))] = path[0]


def get_path_fields(path):
    fields = []
    structs = {}
    _get_path_fields(path, fields, structs)
    return fields, structs


def _realize_conditions(struct):
    conditions = []

    for _condition in struct.conditions:
        conditions.append((struct, _condition))

    for field in struct.fields:
        if isinstance(field, Union):
            for union_struct in field.structs:
                _conditions = _realize_conditions(union_struct)
                for _struct, _condition in _conditions:
                    conditions.append(
                        (
                            (field.__class__, union_struct, _struct),
                            (field.__class__, union_struct, _condition),
                        )
                    )
        elif isinstance(field, Vector):
            _conditions = _realize_conditions(field.klass)
            for _struct, _condition in _conditions:
                conditions.append(
                    (
                        (field.__class__, field.klass, _struct),
                        (field.__class__, field.klass, _condition),
                    )
                )
        elif isinstance(field, Field):
            pass
        elif issubclass(field, Struct):
            _conditions = _realize_conditions(field)
            for _struct, _condition in _conditions:
                conditions.append(((struct, _struct), (struct, _condition)))

    return conditions


def realize_conditions(root_class):
    return _realize_conditions(root_class)


def format_tuple(t):
    def _format_tuple(t):
        if isinstance(t, type):
            return t.__name__
        elif isinstance(t, tuple):
            return tuple(_format_tuple(_) for _ in t)
        else:
            return t

    return _format_tuple(t)
