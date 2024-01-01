class GraphError(RuntimeError):
    pass


class GraphNodeValueError(GraphError):
    pass


class GraphInvalidOpError(GraphError):
    pass


class GraphCycleDetectedError(GraphError):
    pass
