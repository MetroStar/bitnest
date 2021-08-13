from bitnest.field import Struct, UnsignedInteger, Bits, Union, FieldRef, Vector


class CommandWord(Struct):
    fields = [
        UnsignedInteger('remote_terminal_address', 5),
        UnsignedInteger('number_of_words', 3)
    ]


class DataWord(Struct):
    fields = [
        Bits('data', 16),
    ]


class RTToController(Struct):
    name = "Remote Terminal to Controller"

    fields = [
        CommandWord,
        Vector(DataWord, length=FieldRef('CommandWord.number_of_words')),
    ]

    conditions = [
        (FieldRef('CommandWord.remote_terminal_address') == 0x1f)
    ]

class ControllerToRT(Struct):
    name = "Controller to Remote Terminal"

    fields = [
        CommandWord,
    ]

    conditions = [
        (FieldRef('CommandWord.number_of_words') == 0x0)
    ]

class MILSTD_1553_Message(Struct):
    fields = [
        UnsignedInteger('bus_id', 8),
        Union([
            RTToController,
            ControllerToRT,
        ])
    ]
