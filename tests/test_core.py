import pytest

from models.simple import MILSTD_1553_Message
from models.chapter10 import MILSTD_1553_Data_Packet_Format_1

from bitnest.core import realize_datatypes


@pytest.mark.parametrize(
    "struct", [MILSTD_1553_Message, MILSTD_1553_Data_Packet_Format_1]
)
def test_realize_paths(struct):
    realize_datatypes(struct)
