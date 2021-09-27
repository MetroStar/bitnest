import collections

import graphviz

from bitnest.ast.core import Symbol, Expression


def node_label(node_struct):
    """Takes a given Struct and creates a graphviz node label. It uses the
    table structure that graphviz supports. "ports" are used to create
    edges that point to the specific row within the struct.

    <table ...>
      <tr><td>...</td>...</tr>
      ...
      <tr><td>...</td>...</tr>
    </table>

    """
    symbol, struct_name, fields, conditions, additional = node_struct
    header = '<<table border="0" cellborder="1" cellspacing="0">\n'
    title = f'<tr><td port="0" colspan="3"><b>{struct_name}</b></td></tr>'
    footer = "</table>>"
    field_format = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>"
    struct_format = '<tr><td colspan="3" port="{}">{}</td></tr>'
    rows = []
    edges = set()

    for i, field in enumerate(fields[1:], start=1):
        if field[0] == Symbol("field"):
            symbol, field_type, name, offset, size, additional = field
            rows.append(field_format.format(name, field_type, size))
        elif field[0] == Symbol("vector"):
            symbol, struct, length = field
            rows.append(struct_format.format(i, struct[1]))
            edges.add((f"{struct_name}:{i}", struct[1] + ":0"))
        elif field[0] == Symbol("struct"):
            symbol, name, fields, conditions, additional = field
            rows.append(struct_format.format(i, name))
            edges.add((f"{struct_name}:{i}", name + ":0"))
        elif field[0] == Symbol("union"):
            symbol, *structs = field
            rows.append(struct_format.format(i, "union"))
            for struct in structs:
                edges.add((f"{struct_name}:{i}", struct[1] + ":0"))

    node = (struct_name, header + title + "\n".join(rows) + footer)
    return node, edges


def visualize(root_class):
    graph = graphviz.Digraph("structs", node_attr={"shape": "plaintext"})

    visited_nodes = set()
    visited_edges = set()

    for struct in Expression(root_class.expression()).find_symbol(
        Symbol("struct"), order="pre_order"
    ):
        symbol, name, fields, conditions, additional = struct
        if name not in visited_nodes:
            node, edges = node_label(struct)
            graph.node(*node)
            for edge in edges:
                if edge not in visited_edges:
                    graph.edge(*edge)
                    visited_edges.add(edge)
            visited_nodes.add(name)

    return graph
