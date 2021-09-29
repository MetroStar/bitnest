import pytest

from bitnest.core import Symbol, Expression, Variable


@pytest.mark.parametrize(
    "expression,result",
    [
        (
            (Variable("a") + 1 + Variable("b") + 1 + 2),
            Expression(
                (
                    Symbol("add"),
                    (Symbol("variable"), "a"),
                    (Symbol("variable"), "b"),
                    (Symbol("integer"), 4),
                )
            ),
        )
    ],
)
def test_ast_simplify(expression, result):
    assert expression.transform("arithmetic_simplify").expression == result.expression
