from bitnest.field import Struct, Field, Union, Vector


def _realize_datatypes(struct):
    datatypes, conditions = (), []
    for field in struct.fields:
        if isinstance(field, Union):
            for union_struct in field.structs:
                datatypes, conditions = _realize_datatypes(union_struct)
        elif isinstance(field, Vector):
            datatypes, conditions = _realize_datatypes(field.klass)
        elif isinstance(field, Field):
            pass
        elif issubclass(field, Struct):
            datatypes, conditions = _realize_datatypes(field)
    return datatypes, conditions


def realize_datatypes(root_class):
    return _realize_datatypes(root_class)
