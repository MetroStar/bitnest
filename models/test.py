from bitnest.field import Struct, Bits, Union, UnsignedInteger, SignedInteger


class StructD(Struct):
    """All about StructD description"""

    name = "StructD"
    fields = [UnsignedInteger(name="FieldD", nbits=7, help="info about FieldD")]


class StructC(Struct):
    """All about StructC description"""

    name = "StructC"
    fields = [
        StructD,
        Bits(name="FieldC", nbits=4, help="info about FieldC"),
    ]


class StructB(Struct):
    """All about StructB description"""

    name = "StructB"
    fields = [SignedInteger(name="FieldB", nbits=8, help="info about FieldB")]


class StructA(Struct):
    """All about StructA description"""

    name = "StructA"
    fields = [
        Bits(name="FieldA", nbits=4, help="info about FieldA"),
        Union([StructB, StructC]),
        Union([StructB, StructC]),
        Union([StructB, StructC]),
    ]
