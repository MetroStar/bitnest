import operator

import pytest

from bitnest.ast.core import Expression, Variable, UniqueVariable, Symbol


def test_not_expression():
    test_value = True
    v = Variable("test_value")
    expression = ~v
    assert expression.eval(context={"test_value": test_value}) == (not test_value)


def test_and_operator():
    test_value = 1
    other_value = 2
    expression = Variable("test_value") & other_value
    assert expression.eval(context={"test_value": test_value}) == (
        test_value and other_value
    )


def test_or_operator():
    test_value = 1
    other_value = 2
    expression = Variable("test_value") | other_value
    assert expression.eval(context={"test_value": test_value}) == (
        test_value or other_value
    )


@pytest.mark.parametrize(
    "operator",
    [
        operator.add,
        operator.sub,
        operator.mul,
        operator.mod,
        operator.floordiv,
        operator.truediv,
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.ge,
        operator.gt,
    ],
)
def test_binary_expressions(operator):
    test_value = 1
    other_value = 2

    v = Variable("test_value")
    expression = operator(v, other_value)

    assert expression.eval(context={"test_value": test_value}) == operator(
        test_value, other_value
    )


def test_post_order_replacement():
    test_a = 11
    expression = (Variable("test_a") + 1) * 2

    def rewrite_add(symbol, args):
        _args = []
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == Symbol("mul"):
                arg = (Symbol("add"), *arg[1:])
            _args.append(arg)
        return (Symbol("sub"), *_args)

    def rewrite_mul(symbol, args):
        _args = []
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == Symbol("sub"):
                arg = (Symbol("mul"), *arg[1:])
            _args.append(arg)
        return (Symbol("truediv"), *_args)

    # pre order traversal
    # (self, left, ..., right) replacement of nodes
    # (test_a + 1) * 2
    # (mul (<here>add (variable test_a) 1) 2)
    # (test_a - 1) * 2
    # (mul (<here>sub (variable test_a) 1) 2)
    # (test_a * 1) * 2
    # (<here>mul (mul (variable test_a) 1) 2)
    # (test_a * 1) / 2
    # (<here>truediv (mul (variable test_a) 1) 2)

    expression.replace(
        {
            Symbol("add"): rewrite_add,
            Symbol("mul"): rewrite_mul,
        },
        order="post_order",
    )
    assert expression.eval(context={"test_a": test_a}) == ((test_a * 1) / 2)


def test_post_order_replacement():
    test_a = 11
    expression = (Variable("test_a") + 1) * 2

    def rewrite_add(symbol, args):
        _args = []
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == Symbol("mul"):
                arg = (Symbol("add"), *arg[1:])
            _args.append(arg)
        return (Symbol("sub"), *_args)

    def rewrite_mul(symbol, args):
        _args = []
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == Symbol("add"):
                arg = (Symbol("mul"), *arg[1:])
            _args.append(arg)
        return (Symbol("truediv"), *_args)

    expression.replace(
        {
            Symbol("add"): rewrite_add,
            Symbol("mul"): rewrite_mul,
        },
        order="pre_order",
    )

    # post order traversal
    # (left, ..., right, self) replacement of nodes
    # (test_a + 1) * 2
    # (<here>mul (add (variable test_a) 1) 2)
    # (test_a * 1) * 2
    # (<here>mul (mul (variable test_a) 1) 2)
    # (test_a * 1) / 2
    # (<here>truediv (mul (variable test_a) 1) 2)
    # (test_a / 1) / 2
    # (truediv (<here>mul (variable test_a) 1) 2)
    assert expression.eval(context={"test_a": test_a}) == ((test_a / 1) / 2)
