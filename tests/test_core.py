# import pytest

# from models.simple import MILSTD_1553_Message
# from models.chapter10 import MILSTD_1553_Data_Packet_Format_1

# from bitnest.core import realize_datatype, realize_conditions, realize_datatype_paths


# @pytest.mark.parametrize(
#     "struct", [MILSTD_1553_Message, MILSTD_1553_Data_Packet_Format_1]
# )
# def test_realize_paths(struct):
#     datatype = realize_datatype(struct)
#     conditions = realize_conditions(struct)
#     paths = realize_datatype_paths(datatype)
