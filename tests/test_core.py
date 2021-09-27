import pytest

from models.test import StructA
from models.simple import MILSTD_1553_Message
from models.chapter10 import MILSTD_1553_Data_Packet_Format_1

from bitnest.core import realize_datatype_paths
from bitnest.ast.core import Expression


@pytest.mark.parametrize(
    "struct", [StructA, MILSTD_1553_Message, MILSTD_1553_Data_Packet_Format_1]
)
def test_realize_paths(struct):
    datatype = Expression(struct.expression())
    paths = realize_datatype_paths(datatype)
