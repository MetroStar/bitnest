"""Realize all conditions within a given datatype

"""
from bitnest.core import Expression, Symbol


def identify_field_reference(root_struct, field_reference):
    field_reference = Expression(field_reference)
    expression = Expression(root_struct)
    stack = []

    def raise_error(name, struct, stack, expression):
        raise ValueError(
            f"cannot find name={name} within struct={struct} current stack={stack} within expression={expression}"
        )

    for section in field_reference.name.split("."):
        if expression.symbol == Symbol("struct"):
            for field in expression.fields[1:]:
                field = Expression(field)
                if field.symbol == Symbol("vector"):
                    struct = Expression(field.struct)
                    if struct.name == section:
                        stack.append(section)
                        expression = struct
                        break
                elif field.name == section:
                    expression = field
                    stack.append(section)
                    break
            else:
                raise_error(section, root_struct, stack, expression)
        elif expression.symbol == Symbol("field"):
            raise_error(section, root_struct, stack, expression)
        elif expression.symbol == Symbol("vector"):
            struct = Expression(expression.struct)
            if struct.name == section:
                expression = struct
                stack.append(section)
            else:
                raise_error(section, root_struct, stack, expression)

    if expression.symbol != Symbol("field"):
        raise ValueError(
            f"field reference={field_reference} did not resolve to a field in struct={root_struct}"
        )

    return expression


def realize_conditions(struct: Expression) -> Expression:
    current_struct = []
    _struct = Expression(struct)

    def replacement_function(symbol, args):
        if symbol == Symbol("struct"):
            current_struct.append((symbol, *args))

        symbol, args = yield (symbol, *args)

        if symbol == Symbol("struct"):
            current_struct.pop()
        elif symbol == Symbol("field_reference"):
            name, id = args
            field = identify_field_reference(current_struct[-1], (symbol, *args))
            args = name, field.id
        yield (symbol, *args)

    _struct.replace(replacement_function=replacement_function)
    return _struct
