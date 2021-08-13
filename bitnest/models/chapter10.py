"""
Chapter 10 Specification
https://www.irig106.org/docs/106-07/chapter10.pdf

"""
from enum import Enum

from bitnest.types import Struct, UnsignedInteger, SignedInteger, Boolean, BitsEnum, Bits, Union, FieldRef


class RecieveTransmitEnum(enum.Enum):
    RECIEVE = 0x0
    TRANSMIT = 0x1


class TimeTagBitsEnum(enum.Enum):
    LAST_BIT_OF_LAST_WORD_OF_MESSAGE = 0x0
    FIRST_BIT_OF_FIRST_WORD_OF_MESSAGE = 0x1
    LAST_BIT_OF_FIRST_COMMAND_WORD_OF_MESSAGE = 0x2
    RESERVED = 0x3


class BusIdEnum(enum.Enum):
    CHANNEL_A = 0x0
    CHANNEL_B = 0x1


class CommandWord(Struct):
    __name__ = "Command Word"

    fields = [
        UnsignedInteger('remote_terminal_address', 5, help="remote terminal address. a Terminal address of 31 signifying a broadcast type command"),
        BitEnum('recieve_transmit', 1, RecieveTransmitEnum, help="whether the command in a recieve or transmit command"),
        UnsignedInteger('location_sub_address', 5, help="a sub-address of 0 or 31 signifying a Mode Code type command"),
        UnsignedInteger('number_of_words', 5),
    ]


class ModeCommand(CommandWord):
    __name__ = "Mode Command"

    conditions = [
        # location_sub_address = 0 or 31
        (FieldRef('location_sub_address') == 0x0) | (FieldRef('location_sub_address') == 0x1f)
    ]


class BroadcastModeCommand(CommandWord):
    __name__ = "Broadcast Mode Command"

    conditions =  [
        # remote terminal address = 31
        (FieldRef('remote_terminal_address') == 0x1f),
        # location_sub_address = 0 or 31
        (FieldRef('location_sub_address') == 0x0) | (FieldRef('location_sub_address') == 0x1f)
    ]


class TransmitCommand(CommandWord):
    __name__ = "Transmit Command"

    conditions = [
        (FieldRef('recieve_transmit') == RecieveTransmitEnum.TRANSMIT),
    ]


class RecieveCommand(CommandWord):
    __name__ = "Recieve Command"

    conditions = [
        (FieldRef('recieve_transmit') == RecieveTransmitEnum.RECIEVE),
    ]


class BroadcastRecieveCommand(CommandWord):
    __name__ = "Broadcast Recieve Command"

    conditions = [
        # remote terminal address = 31
        (FieldRef('remote_terminal_address') == 0x1f),
        (FieldRef('recieve_transmit') == RecieveTransmitEnum.RECIEVE),
    ]


class BroadcastTransmitCommand(CommandWord):
    __name__ = "Broadcast Transmit Command"

    conditions = [
        # remote terminal address = 31
        (FieldRef('remote_terminal_address') == 0x1f),
        (FieldRef('recieve_transmit') == RecieveTransmitEnum.TRANSMIT),
    ]


class StatusWord(Struct):
    __name__ = "Status Word"

    fields = [
        UnsignedInteger('remote_terminal_address', 5),
        Boolean('message_error'),
        Boolean('instrumentation'),
        Boolean('service_request'),
        Bits('reserved', 3),
        Boolean('broadcast_command_recieved'),
        Boolean('busy'),
        Boolean('subsystem_flag'),
        Boolean('dynamic_bus_acceptance'),
        Boolean('terminal_flag'),
    ]


class GapTimesWord(Struct):
    """
    The Gap Times Word indicates the number of tenths of microseconds
    in length of the internal gaps within a single transaction
    """

    __name__ = "Gap Times Word"

    fields = [
        UnsignedInteger('gap_1', 8, help='measures the time between the command or data word and the first (and only) status word in the message'),
        UnsignedInteger('gap_2', 8, help='For RT-to-RT messages, GAP2 measures the time between the last data word and the second status word'),
    ]


class BlockStatusWord(Struct):
    __name__ = "Block Status Word"

    fields = [
        Bits('reserved', 2, help='reserved bits'),
        BitsEnum('bus_id', 1, BusIdEnum, help='indicates the bus ID for the message'),
        Boolean('message_error', help='indicates a message error was encountered'),
        Boolean('rt_to_rt_transfer', help='indicates a RT to RT transfer; message begins with two command words'),
        Boolean('format_error', help='indicates any illegal gap on the bus other than Response Time Out'),
        Boolean('response_time_out', help='indicates a response time out occurred.  The bit is set if any of the Status Word(s) belonging to this message didn’t arrive within the response time of 14μs defined by MIL-STD-1553B'),
        Bits('reserved', 2, help='reserved bits'),
        Boolean('word_count_error', help='indicates that the number of data words transmitted is different than identified in the command word.  A MIL-STD-1553B Status Word with the busy bit set to true will not cause a Word Count Error.  A transmit command with a response timeout will not cause a Word Count Error'),
        Boolean('sync_type_error', help='indicates an incorrect sync type occurred'),
        Boolean('invalid_word_error', help='indicates an invalid word error occurred.  This includes Manchester decoding errors in the synch pattern or word bits, invalid number of bits in the word, or parity error'),
        Bits('reserved', 2),
    ]


class LengthWord(Struct):
    __name__ = "Length Word"

    fields = [
        UnsignedInteger('length_word_bits', 16, help='length of the message is the total number of bytes in the message.  A message consists of command words, data words, and status words'),
    ]


class MILSTD_1553_Intra_Packet_Data_Header(Struct):
    __name__ = "MIL-STD-1553 Intra-Packet Data Header"

    fields = [
        BlockStatusWord,
        GapTimesWord,
        LengthWord,
    ]


class ControllerToRTTransfer(Struct):
    __name__ = "Controller to Remote Terminal Transfer"

    fields = [
        RecieveCommand,
        Vector(DataWord, length=FieldRef('RecieveCommand.number_of_words')),
        StatusWord
    ]

    conditions = [
        (FieldRef('StatusWord.remote_terminal_address') == 0x31),
    ]



class RTToControllerTransfer(Struct):
    __name__ = "Remote Terminal to Controller Transfer"

    fields = [
        TransmitCommand,
        StatusWord,
        Vector(DataWord, length=FieldRef('TransmitCommand.number_of_words'))
    ]

    conditions = [
        (FieldRef('TransmitCommmand.remote_terminal_address') == 0x31),
    ]


class RTToRTTransfer(Struct):
    __name__ = "Remote Terminal to Remote Terminal Transfer"

    fields = [
        RecieveCommand,
        TransmitCommand,
        StatusWord,
        Vector(DataWord, length=FieldRef('RecieveCommand.number_of_words')),
        StatusWord,
    ]

    conditions = [
        (FieldRef('RecieveCommmand.remote_terminal_address') == 0x31),
        # TODO: Ambiguous (should refer to second entry)
        (FieldRef('StatusWord.remote_terminal_address') == 0x31)
    ]


class ModeCommandWithoutData(Struct):
    __name__ = "Mode Command without Data Word"

    fields = [
        ModeCommand,
        StatusWord
    ]


class ModeCommandWithDataTransmit(Struct):
    __name__ = "Mode Command With Data Word (Transmit)"

    fields = [
        ModeCommand,
        StatusWord,
        DataWord,
    ]


class ModeCommandWithDataRecieve(Struct):
    __name__ = "Mode Command With Data Word (Recieve)"

    fields = [
        ModeCommand,
        DataWord,
        StatusWord,
    ]


class BroadcastControllerToRTTransfer(Struct):
    __name__ = "Broadcast Controller to Remote Terminal(s) Transfer"


    fields = [
        BroadcastRecieveCommand,
        Vector(DataWord, length=FieldRef('BroadcastRecieveCommand.number_of_words'))
    ]


class BroadcastRTToRTTransfer(Struct):
    __name__ = "Broadcast Remote Terminal to Remote Terminal Transfer"

    fields = [
        BroadcastRecieveCommand,
        TransmitCommand,
        StatusWord,
        Vector(DataWord, length=FieldRef('BroadcastRecieveCommand.number_of_words'))
    ]


class BroadcastModeCommandWithoutData(Struct):
    __name__ = "Broadcast Mode Command Without Data Word"

    fields = [
        BroadcastModeCommand
    ]


class BroadcastModeCommandWithData(Struct):
    __name__ = "Broadcast Mode Command With Data"

    fields = [
        BroadcastModeCommand,
        DataWord,
    ]


class MILSTD_1553_Intra_Packet_Header(Struct):
    __name__ = "MIL-STD-1553 Intra-Packet Header"

    fields = [
        UnsignedInteger('intra_packet_time_stamp', 8 * 8),
        MILSTD_1553_Intra_Packet_Data_Header,
        Union([
            ControllerToRTTransfer,
            RTToControllerTransfer,
            RTToRTTransfer,
            ModeCommandWithoutData,
            ModeCommandWithDataTransmit,
            ModeCommandWithDataRecieve,
            BroadcastControllerToRTTransfer,
            BroadcastRTToRTTransfer,
            BroadcastModeCommandWithoutData,
            BroadcastModeCommandWithData,
        ])
    ]


class MILSTD_1553_Data_Packet_Format_1(Struct):
    """MIL-STD-1553 BUS data is packetized in Message Mode, with each
    1553 bus “transaction” recorded as a \"message.\" A transaction is
    a BC-to-RT, RT-to-BC, or RT-to-RT word sequence, starting with the
    command word and including all data and status words that are part
    of the transaction, or a mode code word broadcast.  Multiple
    messages may be encoded into the data portion of a single
    packet.

    """

    __name__ = "MIL-STD-1553 Bus Data Packets, Format 1"

    fields = [
        BitsEnum('time_tag_bits', 2, TimeTagBitsEnum, help="indicate which bit of the MIL-STD-1553 message the Intra-Packet Header time tags"),
        Bits('reserved', 6),
        UnsignedInteger('message_count', 24, help="indicates the binary value of the number of messages included in the packet.  An integral number of complete messages will be in each packe"),
        Vector(MILSTD_1553_Intra_Packet_Header, length=FieldRef('message_count')),
    ]