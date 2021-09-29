import itertools
from typing import Callable, Dict, Generator, List, Optional
import importlib


class Symbol:
    def __init__(self, name: str):
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


def replace_nodes(node, replacement_function: Generator):
    generator = replacement_function(node[0], node[1:])
    node = generator.send(None)

    args = []
    for arg in node[1:]:
        if isinstance(arg, tuple):
            arg = replace_nodes(arg, replacement_function)
        args.append(arg)

    return generator.send((node[0], args))


ATTRIBUTE_MAPPING = {
    Symbol("integer"): ["symbol", "value"],
    Symbol("float"): ["symbol", "value"],
    Symbol("variable"): ["symbol", "name"],
}


class Expression:
    def __init__(self, expression):
        # check if expression is already an `Expression`
        if isinstance(expression, self.__class__):
            self.expression = expression.expression
            return

        # check to make sure all arguments are not `Expression`
        args = []
        for arg in expression:
            if isinstance(arg, self.__class__):
                arg = arg.expression
            args.append(arg)

        self.expression = tuple(args)

    def __str__(self) -> str:
        return str(self.expression)

    def __repr__(self) -> str:
        return f"<Expression {self.__str__()}>"

    def __len__(self):
        return len(self.expression)

    def __getitem__(self, sliced) -> "Expression":
        return Expression(self.expression[sliced])

    @property
    def symbol(self) -> Optional[Symbol]:
        if (
            isinstance(self.expression, tuple)
            and len(self.expression)
            and isinstance(self.expression[0], Symbol)
        ):
            return self.expression[0]
        else:
            return None

    def __getattr__(self, attribute):
        try:
            symbol = self.expression[0]
            return self.expression[ATTRIBUTE_MAPPING[symbol].index(attribute)]
        except Exception:
            raise AttributeError(f"Expression has no attribute={attribute}")

    def _lazy_op(self, op, *args):
        arguments = []
        for arg in args:
            if isinstance(arg, int):
                arg = Integer(arg)
            elif isinstance(arg, float):
                arg = Float(arg)

            if isinstance(arg, self.__class__):
                arguments.append(arg.expression)
            else:
                arguments.append(arg)
        self.expression = (op, *arguments)
        return self

    def replace(
        self,
        replacement_mapping: Dict[Symbol, Callable] = None,
        order: str = "post_order",
        replacement_function: Generator = None,
    ):
        def _replacement_function(symbol, args):
            if symbol == Symbol("quote"):
                yield (symbol, *args)

            if symbol in replacement_mapping and order == "pre_order":
                symbol, args = yield replacement_mapping[symbol](symbol, args)
            else:
                symbol, args = yield (symbol, *args)

            if symbol in replacement_mapping and order == "post_order":
                yield replacement_mapping[symbol](symbol, args)
            else:
                yield (symbol, *args)

        self.expression = replace_nodes(
            self.expression, replacement_function or _replacement_function
        )

    def find(self, match_function: Callable) -> List["Expression"]:
        nodes = []

        def find_function(symbol, args):
            if match_function(symbol, args):
                nodes.append(Expression((symbol, *args)))
            symbol, args = yield (symbol, *args)
            yield (symbol, *args)

        replace_nodes(self.expression, replacement_function=find_function)
        return nodes

    def find_symbol(self, symbol: Symbol, order="post_order") -> List["Expression"]:
        def match_function(_symbol, args):
            return symbol == _symbol

        return self.find(match_function)

    def transform(self, transform_name, *args, **kwargs):
        module = importlib.import_module(f"bitnest.transform.{transform_name}")
        return getattr(module, transform_name)(self, *args, **kwargs)

    def backend(self, backend_name, *args, **kwargs):
        module = importlib.import_module(f"bitnest.backend.{backend_name}")
        return getattr(module, backend_name)(self, *args, **kwargs)

    def analysis(self, analysis_name, *args, **kwargs):
        module = importlib.import_module(f"bitnest.analysis.{analysis_name}")
        return getattr(module, analysis_name)(self, *args, **kwargs)

    # for list of special python methods to overload (not all are needed)
    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    def __invert__(self) -> "Expression":  # logical not
        return self._lazy_op(Symbol("not"), self)

    def __and__(self, other) -> "Expression":  # logical and
        return self._lazy_op(Symbol("and"), self, other)

    def __or__(self, other) -> "Expression":  # logical or
        return self._lazy_op(Symbol("or"), self, other)

    def __add__(self, other) -> "Expression":
        return self._lazy_op(Symbol("add"), self, other)

    def __sub__(self, other) -> "Expression":
        return self._lazy_op(Symbol("sub"), self, other)

    def __mul__(self, other) -> "Expression":
        return self._lazy_op(Symbol("mul"), self, other)

    def __floordiv__(self, other) -> "Expression":
        return self._lazy_op(Symbol("floordiv"), self, other)

    def __truediv__(self, other) -> "Expression":
        return self._lazy_op(Symbol("truediv"), self, other)

    def __mod__(self, other) -> "Expression":
        return self._lazy_op(Symbol("mod"), self, other)

    def __eq__(self, other) -> "Expression":
        return self._lazy_op(Symbol("eq"), self, other)

    def __ne__(self, other) -> "Expression":
        return self._lazy_op(Symbol("ne"), self, other)

    def __lt__(self, other) -> "Expression":
        return self._lazy_op(Symbol("lt"), self, other)

    def __gt__(self, other) -> "Expression":
        return self._lazy_op(Symbol("gt"), self, other)

    def __le__(self, other) -> "Expression":
        return self._lazy_op(Symbol("le"), self, other)

    def __ge__(self, other) -> "Expression":
        return self._lazy_op(Symbol("ge"), self, other)


def quote(value) -> Expression:
    return Expression((Symbol("quote"), value))


def list_(*values) -> Expression:
    return Expression((Symbol("list"), *values))


def Variable(name: str) -> Expression:
    return Expression((Symbol("variable"), name))


__UNIQUE_VARIABLE_PREFIX = "__"
__UNIQUE_VARIABLE_COUNTER = itertools.count()


def UniqueVariable() -> Expression:
    return Expression(
        (
            Symbol("variable"),
            f"{__UNIQUE_VARIABLE_PREFIX}{next(__UNIQUE_VARIABLE_COUNTER)}",
        )
    )


def Integer(value: int) -> Expression:
    return Expression((Symbol("integer"), value))


def Float(value: int) -> Expression:
    return Expression((Symbol("float"), value))
