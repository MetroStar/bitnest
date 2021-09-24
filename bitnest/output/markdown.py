import textwrap
import base64

from bitnest.field import Union, Vector, Field, Struct
from bitnest.core import realize_datatype, realize_datatype_paths, get_path_fields
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


def render_struct_descriptions(struct, visited_structs):
    text, structs = node_section(struct)
    unvisited_structs = structs - visited_structs
    visited_structs = structs | visited_structs
    for _struct in unvisited_structs:
        text += render_struct_descriptions(_struct, visited_structs)
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

    text += render_struct_descriptions(root_class, {root_class})

    if realize:
        datatype = realize_datatype(root_class)
        datatype_paths = realize_datatype_paths(datatype)
        html_tables = []
        for path in datatype_paths:
            html_tables.append(path_table_html(path))
        html_tables_text = "\n\n".join(html_tables)

        text += textwrap.dedent(
            """
            # Realized Structures

            {html_tables_text}
            """
        ).format(html_tables_text=html_tables_text)

    return text
