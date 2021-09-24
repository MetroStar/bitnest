import ast
import enum


from bitnest.lisp import Symbol, Variable, UniqueVariable, Expression


def FieldReference(field_name: str):
    return Expression((Symbol("field_reference"), field_name))


def Field(name, size, field_type, offset=None, **additional):
    return ((Symbol(f"field::{field_type}"), name, offset, size, additional))


def UnsignedInteger(name, size, **kwargs):
    return Field(name=name, size=size, field_type="unsigned_integer", **kwargs)


def SignedInteger(name, size, **kwargs):
    return Field(name=name, size=size, field_type="signed_integer", **kwargs)


def Boolean(name, **kwargs):
    return Field(name=name, size=1, field_type="boolean", **kwargs)


def Bits(name, size, **kwargs):
    return Field(name=name, size=size, field_type="bits", **kwargs)


def BitsEnum(name, size, mapping, **kwargs):
    kwargs['mapping'] = mapping
    return Field(name=name, size=size, **kwargs)


class Struct:
    """Base DataStructure"""

    name = "Struct"

    fields = []

    conditions = []

    @classmethod
    def expression(cls):
        return ('struct', cls.name, cls.fields, cls.conditions)


def Union(structs):
    return (Symbol('union'), *tuple(s.expression() for s in structs))


def Vector(struct, length):
    return ((Symbol('vector'), length, struct.expression()))
