"""
   Support functions for jinjia
"""
from jinja2 import nodes, meta
def find_undeclared_variables_in_order(ast):
    """
        Returns a list of undeclared variables **IN ORDER**,
        unlike the same function from  jinjia.meta
    """

    undeclaredSet = meta.find_undeclared_variables(ast) # undeclared, unordered
    orderedNodes = [
        node.name
        for node in ast.find_all(nodes.Name) # including declared, but in order
        if node.name in undeclaredSet # filter out declared
    ]

    result = []
    seen = set()

    # remove duplicates
    for node in orderedNodes:
        if node in seen:
            continue
        seen.add(node)
        result.append(node)

    return result
