from bitnest.types import Struct, UnsignedInteger, Bits, Union, FieldRef


class CommandWord(Struct):
    fields = [
        UnsignedInteger('remote_terminal_address', 5),
        UnsighedInteger('number_of_words', 3)
    ]


class DataWord(Struct):
    fields = [
        Bits('data', 16),
    ]


class RTToController(Struct):
    __name__ = "Remote Terminal to Controller"

    fields = [
        CommandWord,
        Vector(DataWord, length=FieldRef('CommandWord.number_of_words')),
    ]

    conditions = [
        (FieldRef('CommandWord.remote_terminal_address') == 0x1f)
    ]


class ControllerToRT(Struct):
    __name__ = "Controller to Remote Terminal"

    fields = [
        CommandWord,
    ]


class MILSTD_1553_Message(Struct):
    fields = [
        UnsignedInteger('bus_id', 8),
        Union([
            RTToController,
            ControllerToRT,
        ])
    ]
