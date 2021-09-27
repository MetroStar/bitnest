import ast
import enum
import itertools

import astor


class Symbol:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return isinstance(other, type(self)) and other._name == self._name

    def __copy__(self):
        return type(self)(self._name)

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        return f"{self._name}"


def quote(value):
    return (Symbol("quote"), value)


def list_(*values):
    return (Symbol("list"), *values)


DEFAULT_SYMBOL_MAPPING = {
    Symbol("not"): lambda *args: ast.UnaryOp(ast.Not(), args[0]),
    Symbol("and"): lambda *args: ast.BoolOp(ast.And(), [args[0], args[1]]),
    Symbol("or"): lambda *args: ast.BoolOp(ast.Or(), [args[0], args[1]]),
    Symbol("mod"): lambda *args: ast.BinOp(args[0], ast.Mod(), args[1]),
    Symbol("add"): lambda *args: ast.BinOp(args[0], ast.Add(), args[1]),
    Symbol("sub"): lambda *args: ast.BinOp(args[0], ast.Sub(), args[1]),
    Symbol("mul"): lambda *args: ast.BinOp(args[0], ast.Mult(), args[1]),
    Symbol("floordiv"): lambda *args: ast.BinOp(args[0], ast.FloorDiv(), args[1]),
    Symbol("truediv"): lambda *args: ast.BinOp(args[0], ast.Div(), args[1]),
    Symbol("eq"): lambda *args: ast.Compare(args[0], [ast.Eq()], [args[1]]),
    Symbol("ne"): lambda *args: ast.Compare(args[0], [ast.NotEq()], [args[1]]),
    Symbol("lt"): lambda *args: ast.Compare(args[0], [ast.Lt()], [args[1]]),
    Symbol("gt"): lambda *args: ast.Compare(args[0], [ast.Gt()], [args[1]]),
    Symbol("le"): lambda *args: ast.Compare(args[0], [ast.LtE()], [args[1]]),
    Symbol("ge"): lambda *args: ast.Compare(args[0], [ast.GtE()], [args[1]]),
    Symbol("variable"): lambda *args: ast.Name(args[0].value),
}


def backend_python_ast(node, symbol_mapping=DEFAULT_SYMBOL_MAPPING):
    args = []
    for arg in node[1:]:
        if isinstance(arg, tuple):
            args.append(backend_python_ast(arg, symbol_mapping))
        else:
            if isinstance(arg, (str, int, float, bool, enum.Enum)):
                args.append(ast.Constant(arg))
    return symbol_mapping[node[0]](*args)


def replace_nodes_post_order(node, replacement_function):
    """Post order (left, ..., right, self) replacement of nodes"""
    if node[0] == Symbol("quote"):
        return node

    args = []
    for arg in node[1:]:
        if isinstance(arg, tuple):
            arg = replace_nodes_post_order(arg, replacement_function)
        args.append(arg)

    return replacement_function(node[0], args)


def replace_nodes_pre_order(node, replacement_function):
    """Pre order (self, left, ..., right) replacement of nodes"""
    if node[0] == Symbol("quote"):
        return node

    node = replacement_function(node[0], node[1:])

    args = []
    for arg in node[1:]:
        if isinstance(arg, tuple):
            arg = replace_nodes_pre_order(arg, replacement_function)
        args.append(arg)
    return (node[0], *args)


class Expression:
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return f"<Expression {self.__str__()}>"

    def _lazy_op(self, op, *args):
        arguments = []
        for arg in args:
            if isinstance(arg, self.__class__):
                arguments.append(arg.expression)
            else:
                arguments.append(arg)
        self.expression = (op, *arguments)
        return self

    def to_python_ast(self, symbol_mapping=DEFAULT_SYMBOL_MAPPING):
        return backend_python_ast(self.expression, symbol_mapping)

    def to_python_source(self, symbol_mapping=DEFAULT_SYMBOL_MAPPING):
        expression_ast = self.to_python_ast(symbol_mapping=symbol_mapping)
        return astor.to_source(expression_ast)

    def replace(self, replacement_mapping, order="post_order"):
        def replacement_function(symbol, args):
            if symbol == Symbol("quote"):
                return (symbol, *args)

            if symbol in replacement_mapping:
                return replacement_mapping[symbol](symbol, args)
            return (symbol, *args)

        if order == "post_order":
            self.expression = replace_nodes_post_order(
                self.expression, replacement_function
            )
        elif order == "pre_order":
            self.expression = replace_nodes_pre_order(
                self.expression, replacement_function
            )
        else:
            raise ValueError("replacement ordering={order} not supported")

    def eval(self, symbol_mapping=DEFAULT_SYMBOL_MAPPING, context=None):
        return eval(self.to_python_source(symbol_mapping), context)

    def find(self, match_function, order="post_order"):
        nodes = []

        def find_function(symbol, args):
            if match_function(symbol, args):
                nodes.append((symbol, *args))
            return (symbol, *args)

        if order == "post_order":
            replace_nodes_post_order(self.expression, find_function)
        elif order == "pre_order":
            replace_nodes_pre_order(self.expression, find_function)
        else:
            raise ValueError("replacement ordering={order} not supported")

        return nodes

    def find_symbol(self, symbol: Symbol, order="post_order"):
        def match_function(_symbol, args):
            return symbol == _symbol

        return self.find(match_function, order=order)

    # for list of special python methods to overload (not all are needed)
    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    def __invert__(self):  # logical not
        return self._lazy_op(Symbol("not"), self)

    def __and__(self, other):  # logical and
        return self._lazy_op(Symbol("and"), self, other)

    def __or__(self, other):  # logical or
        return self._lazy_op(Symbol("or"), self, other)

    def __add__(self, other):
        return self._lazy_op(Symbol("add"), self, other)

    def __sub__(self, other):
        return self._lazy_op(Symbol("sub"), self, other)

    def __mul__(self, other):
        return self._lazy_op(Symbol("mul"), self, other)

    def __floordiv__(self, other):
        return self._lazy_op(Symbol("floordiv"), self, other)

    def __truediv__(self, other):
        return self._lazy_op(Symbol("truediv"), self, other)

    def __mod__(self, other):
        return self._lazy_op(Symbol("mod"), self, other)

    def __eq__(self, other):
        return self._lazy_op(Symbol("eq"), self, other)

    def __ne__(self, other):
        return self._lazy_op(Symbol("ne"), self, other)

    def __lt__(self, other):
        return self._lazy_op(Symbol("lt"), self, other)

    def __gt__(self, other):
        return self._lazy_op(Symbol("gt"), self, other)

    def __le__(self, other):
        return self._lazy_op(Symbol("le"), self, other)

    def __ge__(self, other):
        return self._lazy_op(Symbol("ge"), self, other)


class Variable(Expression):
    def __init__(self, name: str):
        super().__init__((Symbol("variable"), name))


class UniqueVariable(Expression):
    symbol_prefix = "__"

    counter = itertools.count()

    def __init__(self):
        super().__init__(
            (Symbol("variable"), f"{self.symbol_prefix}{next(self.counter)}")
        )
