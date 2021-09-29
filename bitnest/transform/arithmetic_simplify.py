"""
Transformation to simplify arithmetic expressions within AST

"""
from bitnest.core import Expression, Symbol, Integer, Float


def simplify_add(symbol, args):
    # expand (+ (+ _1 ...) _2 ...) -> (+ _1 ... _2 ...)
    _args = []
    for arg in args:
        if isinstance(arg, tuple) and arg[0] == Symbol("add"):
            _args.extend(arg[1:])
        else:
            _args.append(arg)

    # simplify (+ _1 _2 (integer 3) (integer 4)) -> (+ _1 _2 (integer 7))
    __args = []
    accumulator = 0
    for arg in _args:
        if isinstance(arg, tuple) and arg[0] == Symbol("integer"):
            accumulator += arg[1]
        elif isinstance(arg, tuple) and arg[0] == Symbol("float"):
            accumulator += arg[1]
        else:
            __args.append(arg)

    if accumulator != 0:
        if isinstance(accumulator, int):
            __args.append(Integer(accumulator).expression)
        else:  # float
            __args.append(Float(accumulator).expression)

    # expression fully simplified (add (float 1.0)) -> (float 1.0)
    if len(__args) == 1:
        return __args[0]

    return (symbol, *__args)


DEFAULT_SIMPLIFY_MAPPING = {
    Symbol("add"): simplify_add,
}


def arithmetic_simplify(
    expression: Expression, simplify_mapping=DEFAULT_SIMPLIFY_MAPPING
) -> Expression:
    _expression = Expression(expression)
    _expression.replace(replacement_mapping=simplify_mapping)
    return _expression
