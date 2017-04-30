"""
   Support functions for jinjia
"""
import builtins
from inspect import getmembers, isbuiltin

from jinja2 import nodes, meta

def find_undeclared_variables_in_order(ast):
    """
        Returns a list of undeclared variables **IN ORDER**,
        unlike the same function from  jinjia.meta
    """

    undeclaredSet = meta.find_undeclared_variables(ast) # undeclared, unordered
    orderedNodes = [
        node
        for node in ast.find_all(nodes.Name) # including declared, but in order
        if node.name in undeclaredSet # filter out declared
    ]

    result = []
    seen = set()

    # remove duplicates
    for node in orderedNodes:
        name = node.name
        if name in seen:
            continue
        seen.add(name)
        result.append(name)

    return result

def get_builtin_names():
    """Returns a set of builtin names"""
    return set([
        func[0]
        for func in getmembers(builtins)
    ])

def filter_out_built_ins(collection):
    """Filters every built in function name from the collection"""
    builtin = get_builtin_names()
    return [
        item
        for item in collection
        if item not in builtin
    ]
