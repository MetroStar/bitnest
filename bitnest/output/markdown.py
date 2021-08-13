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

    table = "TODO: table"
    conditions = '\n\n'.join(f' - {condition}' for condition in struct.conditions)

    section = f"""
    # {struct.name}

    {struct.__doc__}

    ## Structure

    {table}

    ## Conditions

    {conditions}
    """
    return section


def markdown(root_class):
    return node_section(root_class)
