import graphviz

from bitnest.core import Symbol, Expression


def node_label(struct):
    """Takes a given Struct and creates a graphviz node label. It uses the
    table structure that graphviz supports. "ports" are used to create
    edges that point to the specific row within the struct.

    <table ...>
      <tr><td>...</td>...</tr>
      ...
      <tr><td>...</td>...</tr>
    </table>

    """
    header = '<<table border="0" cellborder="1" cellspacing="0">\n'
    title = f'<tr><td port="0" colspan="3"><b>{struct.name}</b></td></tr>'
    footer = "</table>>"
    field_format = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>"
    struct_format = '<tr><td colspan="3" port="{}">{}</td></tr>'
    rows = []
    edges = set()

    for i, field in enumerate(struct.fields[1:], start=1):
        field = Expression(field)
        if field.symbol == Symbol("field"):
            rows.append(field_format.format(field.name, field.field_type, field.size))
        elif field.symbol == Symbol("vector"):
            rows.append(struct_format.format(i, field.struct[1]))
            edges.add((f"{struct.name}:{i}", field.struct[1] + ":0"))
        elif field.symbol == Symbol("struct"):
            rows.append(struct_format.format(i, field.name))
            edges.add((f"{struct.name}:{i}", field.name + ":0"))
        elif field.symbol == Symbol("union"):
            symbol, *structs = field.expression
            rows.append(struct_format.format(i, "union"))
            for _struct in structs:
                edges.add((f"{struct.name}:{i}", _struct[1] + ":0"))

    node = (struct.name, header + title + "\n".join(rows) + footer)
    return node, edges


def visualize(root_struct):
    graph = graphviz.Digraph("structs", node_attr={"shape": "plaintext"})

    visited_nodes = set()
    visited_edges = set()

    for struct in root_struct.expression().find_symbol(
        Symbol("struct"), order="pre_order"
    ):
        if struct.name not in visited_nodes:
            node, edges = node_label(struct)
            graph.node(*node)
            for edge in edges:
                if edge not in visited_edges:
                    graph.edge(*edge)
                    visited_edges.add(edge)
            visited_nodes.add(struct.name)

    return graph
