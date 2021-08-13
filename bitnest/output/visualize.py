import collections

import graphviz

from bitnest.field import Struct, Field, Union, Vector


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
    name = struct.__name__
    header = '<<table border="0" cellborder="1" cellspacing="0">\n'
    title = f'<tr><td port="0" colspan="3"><b>{struct.__name__}</b></td></tr>'
    footer = "</table>>"
    field_format = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>"
    struct_format = '<tr><td colspan="3" port="{}">{}</td></tr>'
    rows = []
    struct_references = collections.defaultdict(list)

    for i, field in enumerate(struct.fields, start=1):
        if isinstance(field, Union):
            for union_struct in field.structs:
                struct_references[union_struct].append(f"{name}:{i}")
            rows.append(struct_format.format(i, field.__class__.__name__))

        elif isinstance(field, Vector):
            struct_references[field.klass].append(f"{name}:{i}")
            rows.append(struct_format.format(i, field.__class__.__name__))
        elif isinstance(field, Field):
            rows.append(
                field_format.format(field.name, field.__class__.__name__, field.nbits)
            )
        elif issubclass(field, Struct):
            struct_references[field].append(f"{name}:{i}")
            rows.append(struct_format.format(i, field.__name__))

    return name, header + title + "\n".join(rows) + footer, struct_references


def visualize(root_class):
    graph = graphviz.Digraph("structs", node_attr={"shape": "plaintext"})
    _visualize(graph, root_class, visited_edges=set())
    return graph


def _visualize(graph, node, visited_edges):
    """Breadth first traversal of all structs mentioned from root
    struct"""
    name, label, struct_references = node_label(node)
    for struct in struct_references:
        for field in struct_references[struct]:
            edge = (field, struct.__name__ + ":0")
            if edge not in visited_edges:
                graph.edge(*edge)
                visited_edges.add(edge)
        _visualize(graph, struct, visited_edges)
    graph.node(name, label)
