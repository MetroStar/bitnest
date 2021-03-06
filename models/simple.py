from bitnest.field import (
    Struct,
    UnsignedInteger,
    Bits,
    Union,
    FieldReference,
    Vector,
)


class CommandWord(Struct):
    name = "CommandWord"

    fields = [
        UnsignedInteger("remote_terminal_address", 5),
        UnsignedInteger("number_of_words", 3),
    ]


class DataWord(Struct):
    name = "DataWord"

    fields = [
        Bits("data", 16),
    ]


class RTToController(Struct):
    name = "Remote Terminal to Controller"

    fields = [
        CommandWord,
        Vector(DataWord, length=FieldReference("CommandWord.number_of_words")),
    ]

    conditions = [(FieldReference("CommandWord.remote_terminal_address") == 0x1F)]


class ControllerToRT(Struct):
    name = "Controller to Remote Terminal"

    fields = [
        CommandWord,
    ]

    conditions = [(FieldReference("CommandWord.number_of_words") == 0x0)]


class MILSTD_1553_Message(Struct):
    """This is a mock specification for a MILSTD 1553 Message to be as
    simple as possible while still representative of the difficulty of
    handling specifications.

    """

    name = "MIL-STD 1553 Mock Message"

    fields = [
        UnsignedInteger("bus_id", 8),
        Union(
            RTToController,
            ControllerToRT,
        ),
    ]
