from bitnest.field import Struct, Vector, Bits, Union

class StructB(Struct):
    name = "StructB"
    fields = [Bits(name="FieldB", nbits=8)]

class StructC(Struct):
    name = "StructC"
    fields = [Bits(name="FieldC", nbits=4)]

class StructA(Struct):
    name = "StructA"
    fields = [
        Bits(name="FieldA", nbits=4),
        Union([StructB, StructC]),
        Union([StructB, StructC]),
        Union([StructB, StructC]),
    ]
