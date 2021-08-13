import pytest

from models.simple import MILSTD_1553_Message
from models.chapter10 import MILSTD_1553_Data_Packet_Format_1

from bitnest.output.visualize import visualize
from bitnest.output.markdown import markdown


@pytest.mark.parametrize('struct', [
    MILSTD_1553_Message,
    MILSTD_1553_Data_Packet_Format_1,
])
def test_visualize_models(struct):
    visualize(MILSTD_1553_Message)


@pytest.mark.parametrize('struct', [
    MILSTD_1553_Message,
    MILSTD_1553_Data_Packet_Format_1,
])
def test_visualize_models(struct):
    print(markdown(struct))
