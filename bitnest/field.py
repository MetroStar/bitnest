class Field:
    def __init__(self, name, nbits):
        self.name = name
        self.nbits = nbits


class UnsignedInteger(Field):
    pass


class SignedInteger(Field):
    pass


class Boolean(Field):
    def __init__(self, name):
        self.name = name
        self.nbits = 1


class BitsEnum(Field):
    pass


class BitsEnum(Field):
    def __init__(self, name, nbits, mapping):
        self.name = name
        self.nbits = nbits
        self.mapping = mapping


class Union(Field):
    pass


class Struct:
    pass


class Vector:
    def __init__(self, klass, length):
        self.klass = klass
        self.length
