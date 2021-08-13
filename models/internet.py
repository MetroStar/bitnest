"""
https://en.wikipedia.org/wiki/Internet_protocol_suite

"""
from bitnest.types import (
    Struct,
    Bits,
)


class EthernetFrame(Struct):
    """https://en.wikipedia.org/wiki/Ethernet_frame

    In computer networking, an Ethernet frame is a data link layer
    protocol data unit and uses the underlying Ethernet physical layer
    transport mechanisms. In other words, a data unit on an Ethernet
    link transports an Ethernet frame as its payload.
    """

    __name__ = "Ethernet Frame"

    fields = [
        Bits(
            "preamble",
            7 * 8,
            help="An Ethernet packet starts with a seven-octet preamble and one-octet start frame delimiter (SFD). The preamble consists of a 56-bit (seven-byte) pattern of alternating 1 and 0 bits, allowing devices on the network to easily synchronize their receiver clocks, providing bit-level synchronization",
        ),
        Bits(
            "start_frame_delimiter",
            8,
            help="provide byte-level synchronization and to mark a new incoming frame",
        ),
        Bits("mac_destination", 6 * 8, help="destination mac address"),
        Bits("mac_source", 6 * 8, help="destination mac address"),
        Bits(
            "tag_8021Q",
            4 * 8,
            help="a four-octet field that indicates virtual LAN (VLAN) membership and IEEE 802.1p priority.",
        ),
        ...,
    ]


class IPv4Frame(Struct):
    """
    https://en.wikipedia.org/wiki/IPv4

    Internet Protocol version 4 (IPv4) is the fourth version of the
    Internet Protocol (IP). It is one of the core protocols of
    standards-based internetworking methods in the Internet and other
    packet-switched networks. IPv4 was the first version deployed for
    production on SATNET in 1982 and on the ARPANET in January
    1983. It is still used to route most Internet traffic today,
    despite the ongoing deployment of a successor protocol, IPv6.
    """

    __name__ = "IPv4 Frame"

    fields = [
        Bits("version", 4, help=""),
        Bits("ihl", 4, help=""),
        Bits("dscp", 6, help=""),
        Bits("ecn", 2, help=""),
        Bits("total_length", 2 * 8, help=""),
        Bits("identification", 2 * 8, help=""),
        Bits("flags", 3, help=""),
        Bits("fragment_offset", 13, help=""),
        Bits("time_to_live", 8, help=""),
        Bits("protocol", 8, help=""),
        Bits("header checksum", 16, help=""),
        Bits("source_ip_address", 4 * 8, help=""),
        Bits("destination_ip_address", 4 * 8, help=""),
        ...,
    ]
