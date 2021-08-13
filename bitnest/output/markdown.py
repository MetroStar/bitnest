import textwrap

from bitnest.field import Union, Vector, Field, Struct


def markdown_table(header, rows):
    column_length = [len(_) for _ in rows]
    if min(column_length) != max(column_length):
        raise ValueError("all rows must have the same number of columns")
    column_length = column_length[0]

    if len(header) != column_length:
        raise ValueError("header columns must match length of rows")

    header = [str(_) for _ in header]
    rows = [[str(c) for c in row] for row in rows]
    column_widths = [len(c) for c in header]

    for row in rows:
        for i, c in enumerate(row):
            column_widths[i] = max(column_widths[i], len(c))

    row_format = "| " + " | ".join([f"{{:<{_}s}}" for _ in column_widths]) + " |\n"
    line_format = "|-" + "-|-".join("-" * _ for _ in column_widths) + "-|\n"

    return (
        row_format.format(*header)
        + line_format
        + "".join(row_format.format(*row) for row in rows)
    )


def markdown_section_link(section):
    return f"[{section}](#{section})"


def node_section(struct):
    """Takes a given Struct and creates a graphviz node label. It uses the
    table structure that graphviz supports. "ports" are used to create
    edges that point to the specific row within the struct.

    # <name of struct>

    <docstring of class>

    ## Structure

    | <attribute> | <data type> | <number of bits> | <help> |
    |-------------|-------------|------------------|--------|
    |             |             |                  |        |

    ## Conditions

     - Condition 1
     - ...

    """

    headers = ["name", "data type", "number of bits", "description"]
    rows = []
    structs = set()

    for field in struct.fields:
        if isinstance(field, Union):
            for union_struct in field.structs:
                if union_struct not in structs:
                    structs.add(union_struct)
            rows.append(
                [
                    "",
                    f'{field.__class__.__name__}[{", ".join(markdown_section_link(s.__name__) for s in field.structs)}]',
                    "",
                    "",
                ]
            )
        elif isinstance(field, Vector):
            if field.klass not in structs:
                structs.add(field.klass)
            rows.append(
                [
                    "",
                    field.__class__.__name__,
                    "",
                    markdown_section_link(field.klass.__name__),
                ]
            )

        elif isinstance(field, Field):
            rows.append(
                [field.name, field.__class__.__name__, field.nbits, field.help or ""]
            )
        elif issubclass(field, Struct):
            if field not in structs:
                structs.add(field)
            rows.append(["", markdown_section_link(field.__name__), "", ""])

    table = markdown_table(headers, rows)
    conditions = "\n\n".join(f" - {condition}" for condition in struct.conditions)

    section = textwrap.dedent(
        """
    # {name}

    {doc}

    ## Structure

    {table}
    """
    )

    conditions_section = textwrap.dedent(
        """
    ## Conditions

    {conditions}
    """
    )

    text = section.format(
        name=struct.__name__,
        doc="\n".join(textwrap.wrap(struct.__doc__ or "")),
        table=textwrap.dedent(table),
    )

    if conditions:
        text += conditions_section.format(conditions=textwrap.dedent(conditions))

    return text, structs


def _markdown(struct, visited_structs):
    text, structs = node_section(struct)
    unvisited_structs = structs - visited_structs
    visited_structs = structs | visited_structs
    for _struct in unvisited_structs:
        text += _markdown(_struct, visited_structs)
    return text


def markdown(root_class):
    return _markdown(root_class, {root_class})
