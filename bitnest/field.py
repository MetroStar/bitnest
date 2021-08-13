import ast
import enum


class FieldRef:
    def __init__(self, name: str):
        self.name = name
        self.operations = ("ref", name)

    def __str__(self):
        expr = self.python_ast(self.operations)
        return ast.unparse(expr)

    @staticmethod
    def python_ast(node):
        operation_map = {
            "ref": lambda *args: args[0],
            "not": lambda *args: ast.UnaryOp(ast.Not(), args[0]),
            "and": lambda *args: ast.BoolOp(ast.And(), [args[0], args[1]]),
            "or": lambda *args: ast.BoolOp(ast.Or(), [args[0], args[1]]),
            "add": lambda *args: ast.BinOp(args[0], ast.Add(), args[1]),
            "sub": lambda *args: ast.BinOp(args[0], ast.Sub(), args[1]),
            "mul": lambda *args: ast.BinOp(args[0], ast.Mul(), args[1]),
            "eq": lambda *args: ast.Compare(args[0], [ast.Eq()], [args[1]]),
            "ne": lambda *args: ast.Compare(args[0], [ast.NotEq()], [args[1]]),
            "lt": lambda *args: ast.Compare(args[0], [ast.Lt()], [args[1]]),
            "gt": lambda *args: ast.Compare(args[0], [ast.Gt()], [args[1]]),
            "le": lambda *args: ast.Compare(args[0], [ast.Le()], [args[1]]),
            "ge": lambda *args: ast.Compare(args[0], [ast.Ge()], [args[1]]),
        }

        args = []
        for arg in node[1:]:
            if isinstance(arg, tuple):
                args.append(FieldRef.python_ast(arg))
            else:
                if isinstance(arg, (str, int, float, enum.Enum)):
                    args.append(ast.Constant(arg))
        return operation_map[node[0]](*args)

    def lazy_op(self, op, *args):
        arguments = []
        for arg in args:
            if isinstance(arg, self.__class__):
                arguments.append(arg.operations)
            else:
                arguments.append(arg)
        self.operations = (op, *arguments)
        return self

    def __not__(self):
        return self.lazy_op("not", self)

    def __and__(self, other):
        return self.lazy_op("and", self, other)

    def __or__(self, other):
        return self.lazy_op("or", self, other)

    def __add__(self, other):
        return self.lazy_op("add", self, other)

    def __sub__(self, other):
        return self.lazy_op("sub", self, other)

    def __mul__(self, other):
        return self.lazy_op("mul", self, other)

    def __eq__(self, other):
        return self.lazy_op("eq", self, other)

    def __ne__(self, other):
        return self.lazy_op("ne", self, other)

    def __lt__(self, other):
        return self.lazy_op("lt", self, other)

    def __gt__(self, other):
        return self.lazy_op("gt", self.operations, other)

    def __le__(self, other):
        return self.lazy_op("le", self.operations, other)

    def __ge__(self, other):
        return self.lazy_op("ge", self.operations, other)


class Field:
    def __init__(self, name, nbits, help=None):
        self.name = name
        self.nbits = nbits
        self.help = help


class UnsignedInteger(Field):
    pass


class SignedInteger(Field):
    pass


class Boolean(Field):
    def __init__(self, name, help=None):
        super().__init__(name, 1, help)


class Bits(Field):
    pass


class BitsEnum(Field):
    def __init__(self, name, nbits, mapping, help=None):
        self.name = name
        self.nbits = nbits
        self.mapping = mapping
        self.help = help


class Union(Field):
    def __init__(self, structs):
        self.structs = structs


class Vector:
    def __init__(self, klass, length):
        self.klass = klass
        self.length = length


class Struct:
    """Base DataStructure"""

    name = "Struct"

    fields = []

    conditions = []
