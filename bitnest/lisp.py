import ast
import enum
import itertools


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
    return (Symbol('quote'), value)


DEFAULT_SYMBOL_MAPPING = {
    Symbol("not"): lambda *args: ast.UnaryOp(ast.Not(), args[0]),
    Symbol("and"): lambda *args: ast.BoolOp(ast.And(), [args[0], args[1]]),
    Symbol("or"): lambda *args: ast.BoolOp(ast.Or(), [args[0], args[1]]),
    Symbol("add"): lambda *args: ast.BinOp(args[0], ast.Add(), args[1]),
    Symbol("sub"): lambda *args: ast.BinOp(args[0], ast.Sub(), args[1]),
    Symbol("mul"): lambda *args: ast.BinOp(args[0], ast.Mult(), args[1]),
    Symbol("div"): lambda *args: ast.BinOp(args[0], ast.Div(), args[1]),
    Symbol("eq"): lambda *args: ast.Compare(args[0], [ast.Eq()], [args[1]]),
    Symbol("ne"): lambda *args: ast.Compare(args[0], [ast.NotEq()], [args[1]]),
    Symbol("lt"): lambda *args: ast.Compare(args[0], [ast.Lt()], [args[1]]),
    Symbol("gt"): lambda *args: ast.Compare(args[0], [ast.Gt()], [args[1]]),
    Symbol("le"): lambda *args: ast.Compare(args[0], [ast.LtE()], [args[1]]),
    Symbol("ge"): lambda *args: ast.Compare(args[0], [ast.GtE()], [args[1]]),
    Symbol("variable"): lambda *args: ast.Name(args[0].value),
}


def backend_python_ast(expression, symbol_mapping=DEFAULT_SYMBOL_MAPPING):
    if isinstance(expression, Expression):
        expression = self.expression

    args = []
    for arg in expression[1:]:
        if isinstance(arg, tuple):
            args.append(backend_python_ast(arg, symbol_mapping))
        else:
            if isinstance(arg, (str, int, float, bool, enum.Enum)):
                args.append(ast.Constant(arg))
    return symbol_mapping[expression[0]](*args)


class Expression:
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return f'<Expression {self.__str__()}>'

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

    # for list of special python methods to overload (not all are needed)
    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    def __not__(self):
        return self._lazy_op(Symbol("not"), self)

    def __and__(self, other):
        return self._lazy_op(Symbol("and"), self, other)

    def __or__(self, other):
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
        return self._lazy_op(Symbol("gt"), self.operations, other)

    def __le__(self, other):
        return self._lazy_op(Symbol("le"), self.operations, other)

    def __ge__(self, other):
        return self._lazy_op(Symbol("ge"), self.operations, other)


class Variable(Expression):
    def __init__(self, name: str):
        super().__init__((Symbol("variable"), name))


class UniqueVariable(Expression):
    symbol_prefix = '__'

    counter = itertools.count()

    def __init__(self):
        super().__init__((Symbol("variable"), f"{self.symbol_prefix}{next(self.counter)}"))
