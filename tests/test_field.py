import pytest

from bitnest.field import FieldRef


@pytest.mark.parametrize(
    "expr",
    [
        FieldRef("A.b"),
        not FieldRef("A.b"),
        FieldRef("A.b") & True,
        FieldRef("A.b") | True,
        FieldRef("A.b") + 1,
        FieldRef("A.b") - 1,
        FieldRef("A.b") * 1,
        FieldRef("A.b") / 1,
        FieldRef("A.b") < 1,
        FieldRef("A.b") <= 1,
        FieldRef("A.b") > 1,
        FieldRef("A.b") >= 1,
        FieldRef("A.b") == 1,
        FieldRef("A.b") != 1,
    ],
)
def test_field_reference(expr):
    str(expr)
