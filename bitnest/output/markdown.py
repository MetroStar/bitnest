import textwrap
import base64

from bitnest.core import Symbol, Expression

# from bitnest.core import realize_paths, realize_offsets
import bitnest.output.visualize


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
    return f"[{section}](#{section.replace(' ', '-')})"


def datatype_table_html(fields, regions):
    num_columns = len(fields)

    current_row, current_column = 0, 0
    rows = []
    row_string = ""

    for position in sorted(regions):
        depth, start, end = position
        if depth == current_row:
            pass
        elif current_column == num_columns:
            rows.append(row_string)
            row_string = ""
            current_row = depth
            current_column = 0
        else:
            row_string += f'<td colspan="{num_columns - current_column}"></td>'
            rows.append(row_string)
            row_string = ""
            current_row = depth
            current_column = 0

        if start > current_column:
            row_string += f'<td colspan="{start - current_column}"></td>'
            current_column = start

        expression = Expression(regions[position])
        if expression.symbol == Symbol("vector"):
            row_string += f'<td colspan="{end - start}">vector</td>'
        elif expression.symbol == Symbol("struct"):
            row_string += f'<td colspan="{end - start}">{expression.name}</td>'

        current_column = end

    if current_column != num_columns:
        row_string += f'<td colspan="{num_columns - current_column}"></td>'

    rows.append(row_string)
    row_string = ""

    for field in fields:
        field = Expression(field)
        row_string += f"<td><div>{field.id}</div><div>{field.field_type}</div><div>{field.name}</div><div>{field.offset}</div><div>{field.size}</div></td>"
    rows.append(row_string)

    table_html = "<table>"
    for row in rows:
        table_html += f"<tr>{row}</tr>"
    table_html += "</table>"
    return table_html


def markdown_struct(struct):
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

    docs = "\n".join(textwrap.wrap(struct.additional.get("help", "")))
    text = f"# {struct.name}" "\n\n" f"{docs}" "\n\n" "## Structure\n\n"

    struct_conditions = []
    for condition in struct.conditions[1:]:
        struct_conditions.append(str(condition))

    headers = ["name", "data type", "number of bits", "description"]
    rows = []

    for field in struct.fields[1:]:
        field = Expression(field)
        if field.symbol == Symbol("field"):
            rows.append(
                [
                    field.name,
                    field.field_type,
                    field.size,
                    field.additional.get("help", ""),
                ]
            )
        elif field.symbol == Symbol("vector"):
            rows.append(["", "vector", "", markdown_section_link(field.struct[1])])
        elif field.symbol == Symbol("struct"):
            rows.append([field.name, "", "", markdown_section_link(field.name)])
        elif field.symbol == Symbol("union"):
            symbol, *structs = field.expression
            rows.append(
                [
                    "",
                    "union",
                    "",
                    ", ".join([markdown_section_link(_[1]) for _ in structs]),
                ]
            )

    text += markdown_table(headers, rows) + "\n"

    if struct_conditions:
        text += textwrap.dedent(
            """
            ## Conditions

            """
        )
        text += "\n".join(f" - `{_}`" for _ in struct.conditions) + "\n\n"
    return text


def markdown(root_struct, visualize=True, realize=True):
    text = ""

    if visualize:
        graph = bitnest.output.visualize.visualize(root_struct)
        image = base64.b64encode(graph.pipe(format="png"))
        text += textwrap.dedent(
            f"""
        # Visualize

        ![image](data:image/png;base64,{image.decode("utf-8")})

        """
        )

    visited_structs = set()
    for struct in root_struct.expression().find_symbol(
        Symbol("struct"), order="pre_order"
    ):
        struct = Expression(struct)
        if struct.name not in visited_structs:
            text += markdown_struct(struct)
            visited_structs.add(struct.name)

    if realize:
        datatypes = (
            root_struct.expression()
            .transform("realize_datatypes")
            .transform("realize_conditions")
            .transform("realize_offsets")
            .transform("arithmetic_simplify")
            .analysis("inspect_datatypes")
        )
        text += "\n# Realized Structures\n"
        for i, (datatype, fields, conditions, regions) in enumerate(datatypes, start=1):
            html_table = datatype_table_html(fields, regions)
            text += textwrap.dedent(
                """

                ## Structure {i}

                {html_table}

                """
            ).format(i=i, html_table=html_table)

            if conditions:
                text_conditions = "\n".join(
                    [f" - {condition}" for condition in conditions]
                )
                text += textwrap.dedent(
                    """

                    ### Conditions

                    {text_conditions}

                    """
                ).format(text_conditions=text_conditions)

    return text
