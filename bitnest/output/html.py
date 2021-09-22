from bitnest.field import Struct, Vector, Field
from bitnest.core import get_path_fields


def path_html(path):
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
    rows.append(row_string)
    row_string = ""

    for field in fields:
        row_string += f'<td>{field.name} {field.nbits}</td>'
    rows.append(row_string)

    table_html = "<table>"
    for row in rows:
        table_html += f"<tr>{row}</tr>"
    table_html += "</table>"
    return table_html
