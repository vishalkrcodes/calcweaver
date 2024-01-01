from contextlib import contextmanager

from .utils import logger, FrozenDict


__BASE_GRAPH = {}
__TWEAKS_GRAPH_STACK = []


def get_graphs():
    global __TWEAKS_GRAPH_STACK
    return __TWEAKS_GRAPH_STACK


def get_base_graph():
    global __BASE_GRAPH
    return __BASE_GRAPH


def is_graph_layer_set():
    return len(get_graphs()) > 0


def get_current_graph():
    if is_graph_layer_set():
        return get_graphs()[-1]
    return None


def iter_graphs(reverse=True):
    if reverse:
        for g in reversed(get_graphs()):
            yield g
    else:
        for g in get_graphs():
            yield g


@contextmanager
def context(name=None):
    graphs = get_graphs()
    graphs.append({})
    logger.info("Entering context %s", name)
    try:
        yield
    finally:
        logger.info("Exiting context %s", name)
        graphs.pop()


# a -> b : a depends on b : a connects to b
class Node:
    __slots__ = ("_value", "_connect_to", "_connect_from", "_hash")

    def __init__(self, value):
        self._value = value
        self._connect_to = {}
        self._connect_from = {}
        self._hash = None

    def add_connectto(self, node):
        self._connect_to[hash(node)] = node

    def add_connctfrom(self, node):
        self._connect_from[hash(node)] = node

    def freeze(self):
        self._connect_from = FrozenDict(self._connect_from)
        self._connect_to = FrozenDict(self._connect_to)

    @property
    def value(self):
        return self._value

    def __hash__(self):
        if not self._hash:
            self._hash = hash(self._value)
        return self._hash

    def children(self):
        for node in self._connect_to.values():
            yield node

    def parents(self):
        for node in self._connect_from.values():
            yield node

    def __str__(self) -> str:
        return f"Node:{id(self)}:{self._value}"
