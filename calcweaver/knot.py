from collections import deque

from .error import GraphNodeValueError, GraphInvalidOpError
from .graph import is_graph_layer_set, get_current_graph, get_base_graph, iter_graphs
from .utils import getvalue_or_raise, transform_args_for_hash, logger


class KnotTweak:
    __slots__ = ("_tweakvalue", "_error")

    def __init__(self, tweakvalue):
        self._tweakvalue = tweakvalue
        self._error = None

    @property
    def tweakvalue(self):
        if self._error:
            raise self._error
        return self._tweakvalue


class Knot:
    def __init__(self, default=None, cls_type=None, func=None) -> None:
        self._default = default
        self._value = {}
        self._value_set = {}
        self._func = None
        self.cls_type = cls_type
        if func:
            self._func = func

    @property
    def func(self):
        return self._func

    def setvalue(self, value, obj, hashable_args):
        self._value_set.setdefault(id(obj), {})[hashable_args] = True
        self._value.setdefault(id(obj), {})[hashable_args] = value

    def clear(self, obj):
        if not is_graph_layer_set():
            self._value_set
            self._value.pop(id(obj))

    def get_parent_nodes(self):
        base_graph = get_base_graph()
        node = base_graph[self]
        for curr in node.parents():
            yield curr.value

    def get_dependent_knots(self):
        base_graph = get_base_graph()
        node = base_graph[self]
        for curr in node.children():
            yield curr.value

    def __call__(self, obj, *fargs, **fkwargs):
        # Handle tweak, context, layer
        hashable_args = transform_args_for_hash(*fargs, **fkwargs)
        if is_graph_layer_set():
            current_graph = get_current_graph()
            try:
                current_tweak = current_graph.get(self, {}).get(
                    id(obj), {}).get(hashable_args)
            except TypeError as e:
                raise GraphInvalidOpError(
                    "Knot func arguments must be immutable and hashable!") from e
            if current_tweak:
                return current_tweak.tweakvalue, False
        # Trigger all dependencies
        # Need to track args, kwargs for dependents?
        for knot in self.get_dependent_knots():
            try:
                knot(obj)
            except TypeError:
                logger.warn("Can't pre-execute %s", knot)
                logger.warn("Only static dependencies can be pre-executed!")
        func = self._func
        # Check if any dependencies exist in current layer. If yes, recalculate
        if self._func and is_graph_layer_set():
            current_graph = get_current_graph()
            # Need to find dependent knots with right args, kwargs?
            for knot in self.get_dependent_knots():
                if current_graph.get(knot, {}).get(id(obj)):
                    return func(obj, *fargs, **fkwargs), True

        for graph in iter_graphs():
            tweak = graph.get(self, {}).get(id(obj))
            if isinstance(tweak, KnotTweak):
                return tweak.tweakvalue, False

        if self._value_set.get(id(obj), {}).get(hashable_args):
            return getvalue_or_raise(self._value[id(obj)][hashable_args]), False
        if func:
            try:
                calculated_value = func(obj, *fargs, **fkwargs)
            except Exception as e:
                self.setvalue(GraphNodeValueError(e), obj)
                raise GraphNodeValueError(
                    f"Unable to compute {obj} -> {func.__name__}") from e
            self.setvalue(calculated_value, obj, hashable_args)
            return calculated_value, False
        return getvalue_or_raise(self._value.get(id(obj), {}).get(hashable_args, self._default)), False


class KnotRef:
    def __init__(self, obj, knot):
        self._obj = obj
        self._knot = knot

    def __call__(self, *fargs, **fkwargs):
        value, set_in_graph = self._knot(self._obj, *fargs, **fkwargs)
        if set_in_graph:
            self.tweak(value, *fargs, **fkwargs)
        return value

    def tweak(self, tweakvalue, *fargs, **fkwargs):
        if not is_graph_layer_set():
            raise GraphNodeValueError(
                "Tweak can only be set within graph context/layer!")
        hashable_args = transform_args_for_hash(*fargs, **fkwargs)
        self.clear()
        current_graph = get_current_graph()
        current_graph.setdefault(self._knot, {}).setdefault(id(self._obj), {})[
            hashable_args] = KnotTweak(tweakvalue)

    def clear(self):
        base_graph = get_base_graph()
        dependents = set()
        q = deque()
        member_node = base_graph[self._knot]
        dependents.add(member_node)
        q.extend(member_node.parents())
        while q:
            curr = q.popleft()
            dependents.add(curr)
            for n in curr.parents():
                if n not in dependents:
                    q.append(n)
        if is_graph_layer_set():
            current_graph = get_current_graph()
            for dependent in dependents:
                current_graph.get(dependent.value, {}).pop(id(self._obj), None)
        else:
            for dependent in dependents:
                dependent.clear(self._obj)


def knot(func, default=None):
    return Knot(default=default, func=func)
