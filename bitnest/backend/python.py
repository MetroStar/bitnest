import ast
import functools

import astor

from bitnest.core import Symbol, Expression


def binary_operation(symbol, args):
    operation_map = {
        Symbol("add"): ast.Add,
        Symbol("sub"): ast.Sub,
        Symbol("mul"): ast.Mult,
        Symbol("floordiv"): ast.FloorDiv,
        Symbol("truediv"): ast.Div,
    }
    return functools.reduce(
        lambda left, right: ast.BinOp(left, operation_map[symbol](), right), args
    )


DEFAULT_SYMBOL_MAPPING = {
    Symbol("not"): lambda symbol, args: ast.UnaryOp(ast.Not(), args[0]),
    Symbol("logical_and"): lambda symbol, args: ast.BoolOp(
        ast.And(), [args[0], args[1]]
    ),
    Symbol("logical_or"): lambda symbol, args: ast.BoolOp(ast.Or(), [args[0], args[1]]),
    Symbol("bit_and"): lambda symbol, args: ast.BinOp(args[0], ast.BitAnd(), args[1]),
    Symbol("bit_or"): lambda symbol, args: ast.BinOp(args[0], ast.BitOr(), args[1]),
    Symbol("mod"): lambda symbol, args: ast.BinOp(args[0], ast.Mod(), args[1]),
    Symbol("add"): binary_operation,
    Symbol("sub"): binary_operation,
    Symbol("mul"): binary_operation,
    Symbol("floordiv"): binary_operation,
    Symbol("truediv"): binary_operation,
    Symbol("eq"): lambda symbol, args: ast.Compare(args[0], [ast.Eq()], [args[1]]),
    Symbol("ne"): lambda symbol, args: ast.Compare(args[0], [ast.NotEq()], [args[1]]),
    Symbol("lt"): lambda symbol, args: ast.Compare(args[0], [ast.Lt()], [args[1]]),
    Symbol("gt"): lambda symbol, args: ast.Compare(args[0], [ast.Gt()], [args[1]]),
    Symbol("le"): lambda symbol, args: ast.Compare(args[0], [ast.LtE()], [args[1]]),
    Symbol("ge"): lambda symbol, args: ast.Compare(args[0], [ast.GtE()], [args[1]]),
    Symbol("variable"): lambda symbol, args: ast.Name(args[0]),
    Symbol("integer"): lambda symbol, args: ast.Constant(args[0]),
    Symbol("float"): lambda symbol, args: ast.Constant(args[0]),
    Symbol("enum"): lambda symbol, args: ast.Constant(args[0].value),
    Symbol("index"): lambda symbol, args: ast.Subscript(
        value=args[0], slice=ast.Slice(lower=args[1], upper=args[2])
    ),
    Symbol("assign"): lambda symbol, args: ast.Assign(targets=[args[0]], value=args[1]),
    Symbol("if"): lambda symbol, args: ast.If(test=args[0], body=[args[1]], orelse=[]),
    Symbol("statements"): lambda symbol, args: [_ for _ in args],
}


def to_python_ast(expression: Expression) -> ast.AST:
    _expression = Expression(expression)
    _expression.replace(replacement_mapping=DEFAULT_SYMBOL_MAPPING, order="post_order")
    return _expression.expression


def python(expression: Expression) -> str:
    expression_ast = to_python_ast(expression)

    # terminate statements which render as lists in ast
    if isinstance(expression_ast, list):
        expression_ast = ast.Module(expression_ast)

    return astor.to_source(expression_ast)
