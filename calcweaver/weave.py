from .graph import get_base_graph
from .knot import KnotRef
from .parser import create_template_graph, get_knot_members


class Weave:
    def __init_subclass__(cls) -> None:
        graphs = get_base_graph()
        if cls not in graphs:
            # creates "Pure" members which don't belong to any instance
            cls_graph = create_template_graph(cls)
            graphs[cls] = cls_graph

    def __init__(self):
        cls_members = get_knot_members(self)
        for name, member in cls_members:
            setattr(self, name, KnotRef(self, member))
