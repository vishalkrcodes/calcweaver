import ast
import inspect

from .error import GraphCycleDetectedError
from .knot import Knot, KnotRef
from .graph import Node, get_base_graph
from .utils import logger, check_cycle


def _predicate_knot(value):
    return isinstance(value, Knot)


def _predicate_knotref(value):
    return isinstance(value, KnotRef)


def connect_graph(edges, nodes):
    for start, end in edges:
        nodes[start].add_connectto(nodes[end])
        nodes[end].add_connctfrom(nodes[start])


def getFuncSource(func):
    if func:
        return inspect.cleandoc(inspect.getsource(func))
    return None


def get_knot_members(obj_or_type):
    return inspect.getmembers(obj_or_type, predicate=_predicate_knot)


def get_knotref_members(obj_or_type):
    return inspect.getmembers(obj_or_type, predicate=_predicate_knotref)


def create_template_graph(cls):
    logger.debug("Template graph init %s", cls)
    knots = get_knot_members(cls)
    root, edges, graph_nodes = Node(cls), set(), dict()
    for name, knot in knots:
        knot._name = f"{cls.__name__}.{name}"
        knot.cls_type = cls
        knot_node = Node(knot)
        root.add_connectto(knot_node)
        graph_nodes[name] = knot_node
        source = getFuncSource(knot.func)
        if not source:
            logger.debug("%s has no dependency!", name)
            continue
        nodes = ast.walk(ast.parse(source))
        fndef = next(nodes)
        while not isinstance(fndef, ast.FunctionDef):
            fndef = next(nodes)
        self_keyword = fndef.args.args[0].arg
        # print(ast.dump(ast.parse(source), indent=4))
        for node in nodes:
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.value.id == self_keyword:
                    dependency_node_name = str(node.func.attr)
                    logger.debug("%s depends on %s.%s", name,
                                 self_keyword, dependency_node_name)
                    edges.add((name, dependency_node_name))
    connect_graph(set(edges), graph_nodes)
    if check_cycle(root):
        raise GraphCycleDetectedError("Cycle detected in %s", cls)
    base_graph = get_base_graph()
    for node in graph_nodes.values():
        base_graph[node.value] = node
    return root
