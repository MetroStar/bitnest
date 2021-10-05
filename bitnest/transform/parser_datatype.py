import functools

from bitnest.core import Expression, Symbol, Variable, if_, assign, statements, Integer


def parser_datatype(
    expression: Expression,
    bits_name: str = "__bits",
    datatype_mask_name: str = "__datatype_mask",
) -> Expression:
    _expression = Expression(expression)

    _statements = [
        assign(Variable(datatype_mask_name), Integer(0)),
    ]
    datatypes = _expression.analysis("inspect_datatypes")

    for i, (datatype, fields, conditions, regions) in enumerate(datatypes):
        field_mapping = {}
        for field in fields:
            field = Expression(field)
            field_mapping[field.id] = field

        def handle_field_reference(symbol, args, field_mapping):
            name, id = args
            size = Expression(field_mapping[id].size)
            offset = Expression(field_mapping[id].offset)

            return (
                Symbol("index"),
                Variable(bits_name).expression,
                offset.expression,
                (offset + size).expression,
            )

        replacement_mapping = {
            Symbol("field_reference"): functools.partial(
                handle_field_reference, field_mapping=field_mapping
            )
        }

        _conditions = []
        for condition in conditions:
            condition_expression = Expression(condition)
            condition_expression.replace(
                replacement_mapping=replacement_mapping, order="pre_order"
            )
            _conditions.append(condition_expression)

        _statements.append(
            if_(
                functools.reduce(
                    lambda left, right: (Symbol("and"), left, right), _conditions
                ),
                assign(
                    Variable(datatype_mask_name),
                    Expression(
                        (
                            Symbol("bit_or"),
                            Variable(datatype_mask_name),
                            Integer(2 ** i),
                        )
                    ),
                ),
            )
        )

    return Expression(statements(*_statements))
