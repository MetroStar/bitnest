from bitnest.ast.core import Symbol, Expression, list_


def FieldReference(field_name: str):
    return Expression((Symbol("field_reference"), field_name))


def Field(name, size, field_type, offset=None, **additional):
    return (Symbol("field"), field_type, name, offset, size, additional)


def UnsignedInteger(name, size, **kwargs):
    return Field(name=name, size=size, field_type="unsigned_integer", **kwargs)


def SignedInteger(name, size, **kwargs):
    return Field(name=name, size=size, field_type="signed_integer", **kwargs)


def Boolean(name, **kwargs):
    return Field(name=name, size=1, field_type="boolean", **kwargs)


def Bits(name, size, **kwargs):
    return Field(name=name, size=size, field_type="bits", **kwargs)


def BitsEnum(name, size, mapping, **kwargs):
    kwargs["mapping"] = mapping
    return Field(name=name, size=size, field_type="bits_enum", **kwargs)


class Struct:
    """Base DataStructure"""

    name = "Struct"

    fields = []

    conditions = []

    @classmethod
    def expression(cls):
        fields = []
        for field in cls.fields:
            if isinstance(field, type) and issubclass(field, Struct):
                fields.append(field.expression())
            else:
                fields.append(field)

        conditions = []
        for condition in cls.conditions:
            if isinstance(condition, Expression):
                conditions.append(condition.expression)
            else:
                conditions.append(condition)

        return (
            Symbol("struct"),
            cls.name,
            list_(*fields),
            list_(*cls.conditions),
            {"help": cls.__doc__ or ""},
        )


def Union(*structs):
    return (Symbol("union"), *tuple(s.expression() for s in structs))


def Vector(struct, length):
    return (Symbol("vector"), struct.expression(), length)
