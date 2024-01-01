import graphviz
from collections import deque

from .error import GraphInvalidOpError
from .graph import get_base_graph, get_current_graph
from .knot import Knot, KnotRef
from .parser import get_knot_members, get_knotref_members
from .weave import Weave


def get_weavetype_digraph(weavetype):
    typename = graphviz.escape(weavetype.__name__)
    graph = graphviz.Digraph(
        typename, comment="%s dependency graph" % (str(type(weavetype)), ))
    graph.node(typename, label="%s :: %s" % (typename, weavetype))
    for name, knot in get_knot_members(weavetype):
        graph.node(str(knot), label="%s :: %s" % (name, knot))
        graph.edge(typename, str(knot))
        for child in knot.get_dependent_knots():
            graph.edge(str(knot), str(child))
    return graph

# def get_knot_digraph(knot):
#     graph = graphviz.Digraph(str(knot), comment = "Knot dependency graph")
#     graph.node(str(knot))
#     for child in knot.children():
#             graph.node()
#             graph.edge(str(knot), str(child))


def get_digraph(obj):
    try:
        if issubclass(obj, Weave):
            return get_weavetype_digraph(obj)
        else:
            raise GraphInvalidOpError("Can only visualize Weave or Knot!")
    except TypeError:
        raise
