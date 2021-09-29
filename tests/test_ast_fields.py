import enum

import pytest

from bitnest import field


class AnEnum(enum.Enum):
    A = 0x1
    B = 0x2


class AStruct(field.Struct):
    name = "AStruct"

    fields = [
        field.Bits("somebits", 11),
    ]

    conditions = [field.FieldReference("somebits") == 0x1]


@pytest.mark.parametrize(
    "field,args",
    [
        (field.FieldReference, ("a_field",)),
        (field.Field, ("a_field", 10, "atype")),
        (field.UnsignedInteger, ("uint", 13)),
        (field.SignedInteger, ("sint", 9)),
        (field.Boolean, ("aboolean",)),
        (field.Bits, ("somebits", 19)),
        (field.BitsEnum, ("anenum", 2, AnEnum)),
    ],
)
def test_create_field(field, args):
    field(*args)


def test_struct():
    AStruct.expression()


def test_union():
    field.Union(AStruct)


def test_vector():
    field.Vector(AStruct, field.FieldReference("somebits") * 2)
