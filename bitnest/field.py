from typing import List


from bitnest.core import (
    Symbol,
    UniqueVariable,
    Expression,
    list_,
    Integer,
    ATTRIBUTE_MAPPING,
)


ATTRIBUTE_MAPPING.update(
    {
        Symbol("field_reference"): ["symbol", "name"],
        Symbol("field"): [
            "symbol",
            "field_type",
            "name",
            "offset",
            "size",
            "additional",
        ],
        Symbol("struct"): ["symbol", "name", "fields", "conditions", "additional"],
        Symbol("vector"): ["symbol", "struct", "length", "loop_variable"],
    }
)


def FieldReference(field_name: str):
    return Expression((Symbol("field_reference"), field_name))


def Field(name: str, size: int, field_type: str, offset=None, **additional):
    return Expression(
        (Symbol("field"), field_type, name, offset, Integer(size), additional)
    )


def UnsignedInteger(name: str, size: int, **kwargs):
    return Field(name=name, size=size, field_type="unsigned_integer", **kwargs)


def SignedInteger(name: str, size: int, **kwargs):
    return Field(name=name, size=size, field_type="signed_integer", **kwargs)


def Boolean(name: str, **kwargs):
    return Field(name=name, size=1, field_type="boolean", **kwargs)


def Bits(name: str, size: int, **kwargs):
    return Field(name=name, size=size, field_type="bits", **kwargs)


def BitsEnum(name: str, size: int, mapping, **kwargs):
    kwargs["mapping"] = mapping
    return Field(name=name, size=size, field_type="bits_enum", **kwargs)


class Struct:
    """Base DataStructure"""

    name = "Struct"

    fields = []

    conditions = []

    @classmethod
    def expression(cls) -> Expression:
        fields = []
        for field in cls.fields:
            if isinstance(field, type) and issubclass(field, Struct):
                fields.append(field.expression().expression)
            elif isinstance(field, Expression):
                fields.append(field.expression)
            else:
                fields.append(field)

        conditions = []
        for condition in cls.conditions:
            if isinstance(condition, Expression):
                conditions.append(condition.expression)
            else:
                conditions.append(condition)

        return Expression(
            (
                Symbol("struct"),
                cls.name,
                list_(*fields),
                list_(*cls.conditions),
                {"help": cls.__doc__ or ""},
            )
        )


def Union(*structs: List[Struct]) -> Expression:
    return Expression((Symbol("union"), *tuple(s.expression() for s in structs)))


def Vector(struct: Struct, length: Expression) -> Expression:
    return Expression(
        (Symbol("vector"), struct.expression(), length.expression, UniqueVariable())
    )
