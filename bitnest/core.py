from bitnest.field import Struct, Field, Union, Vector


def _realize_datatype(struct):
    datatype, conditions = [
        struct,
    ], []

    for _condition in struct.conditions:
        conditions.append((struct, _condition))

    for field in struct.fields:
        if isinstance(field, Union):
            union_datatype = [field.__class__]
            for union_struct in field.structs:
                _datatype, _conditions = _realize_datatype(union_struct)
                for _struct, _condition in _conditions:
                    conditions.append(
                        (
                            (field.__class__, union_struct, _struct),
                            (field.__class__, union_struct, _condition),
                        )
                    )
                union_datatype.append(_datatype)
            datatype.append(union_datatype)
        elif isinstance(field, Vector):
            _datatype, _conditions = _realize_datatype(field.klass)
            for _struct, _condition in _conditions:
                conditions.append(
                    (
                        (field.__class__, field.klass, _struct),
                        (field.__class__, field.klass, _condition),
                    )
                )
            datatype.append((field.__class__, field.klass, _datatype))
        elif isinstance(field, Field):
            datatype.append(field.__class__)
        elif issubclass(field, Struct):
            _datatype, _conditions = _realize_datatype(field)
            for _struct, _condition in _conditions:
                conditions.append(((struct, _struct), (struct, _condition)))
            datatype.append(_datatype)
    return tuple(datatype), conditions


def realize_datatype(root_class):
    return _realize_datatype(root_class)
