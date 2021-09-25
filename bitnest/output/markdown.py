import textwrap
import base64

from bitnest.ast.core import Symbol, Expression
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


def path_table_html(path):
    fields, structs = get_path_fields(path)
    num_columns = len(fields)

    current_row, current_column = 0, 0
    rows = []
    row_string = ""

    for position in sorted(structs):
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

        row_string += f'<td colspan="{end - start}">{structs[position].name}</td>'
        current_column = end

    if current_column != num_columns:
        row_string += f'<td colspan="{num_columns - current_column}"></td>'

    rows.append(row_string)
    row_string = ""

    for field in fields:
        row_string += f"<td>{field.name} {field.nbits}</td>"
    rows.append(row_string)

    table_html = "<table>"
    for row in rows:
        table_html += f"<tr>{row}</tr>"
    table_html += "</table>"
    return table_html


def markdown_struct(struct_node):
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

    symbol, name, fields, conditions, additional = struct_node
    docs = "\n".join(textwrap.wrap(additional.get("help", "")))
    text = f"# {name}" "\n\n" f"{docs}" "\n\n" "## Structure\n\n"

    struct_conditions = []
    for condition in conditions[1:]:
        struct_conditions.append(str(condition))

    headers = ["name", "data type", "number of bits", "description"]
    rows = []

    for field in fields[1:]:
        if field[0] == Symbol("field"):
            symbol, field_type, name, offset, size, additional = field
            rows.append([name, field_type, size, additional.get("help", "")])
        elif field[0] == Symbol("vector"):
            symbol, struct, length = field
            rows.append(["", "vector", "", markdown_section_link(struct[1])])
        elif field[0] == Symbol("struct"):
            symbol, name, fields, conditions, additional = field
            rows.append([name, "", "", markdown_section_link(name)])
        elif field[0] == Symbol("union"):
            symbol, *structs = field
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
        text += "\n".join(f" - `{_}`" for _ in struct_conditions) + "\n\n"
    return text


def markdown(root_class, visualize=True, realize=True):
    text = ""

    if visualize:
        graph = bitnest.output.visualize.visualize(root_class)
        image = base64.b64encode(graph.pipe(format="png"))
        text += textwrap.dedent(
            f"""
        # Visualize

        ![image](data:image/png;base64,{image.decode("utf-8")})

        """
        )

    visited_structs = set()
    for struct in Expression(root_class.expression()).find_symbol(
        Symbol("struct"), order="pre_order"
    ):
        name = struct[1]
        if name not in visited_structs:
            text += markdown_struct(struct)
            visited_structs.add(struct[1])

    # text += render_struct_descriptions(root_class, {root_class})

    # if realize:
    #     datatype = realize_datatype(root_class)
    #     datatype_paths = realize_datatype_paths(datatype)
    #     html_tables = []
    #     for path in datatype_paths:
    #         html_tables.append(path_table_html(path))
    #     html_tables_text = "\n\n".join(html_tables)

    #     text += textwrap.dedent(
    #         """
    #         # Realized Structures

    #         {html_tables_text}
    #         """
    #     ).format(html_tables_text=html_tables_text)

    return text
