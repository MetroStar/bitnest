import pytest

from models.test import StructA
from models.simple import MILSTD_1553_Message
from models.chapter10 import MILSTD_1553_Data_Packet_Format_1


@pytest.mark.parametrize(
    "struct", [StructA, MILSTD_1553_Message, MILSTD_1553_Data_Packet_Format_1]
)
def test_realize_paths(struct):
    expression = struct.expression()
    source = (
        expression.transform("realize_datatypes")
        .transform("realize_conditions")
        .transform("realize_offsets")
        .transform("parser_datatype")
        .transform("arithmetic_simplify")
        .backend("python")
    )
