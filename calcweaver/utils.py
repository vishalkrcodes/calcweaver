from .error import GraphError, GraphInvalidOpError
import logging
import os


logger = logging.getLogger("calcweaver")

log_level_set = os.getenv("CALCWEAVER_LOG_LEVEL", "info")

log_level = None

if log_level_set == "debug":
    log_level = logging.DEBUG
if log_level_set == "info":
    log_level = logging.INFO
elif log_level_set == "warn" or log_level_set == "warning":
    log_level = logging.WARN
elif log_level_set == "error":
    log_level = logging.ERROR
else:
    log_level = logging.INFO

logger.setLevel(log_level)


class FrozenDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        raise GraphInvalidOpError("Trying to set a new item on Frozen dict!")


def getvalue_or_raise(value):
    if isinstance(value, GraphError):
        raise value
    return value


def __check_cycle_dfs(node, visited, rec_stack):
    visited[node] = True
    rec_stack[node] = True
    for child in node.children():
        if not visited.get(child):
            if __check_cycle_dfs(child, visited, rec_stack):
                return True
        elif rec_stack.get(child):
            return True
    rec_stack[node] = False
    return False


def check_cycle(root):
    return __check_cycle_dfs(root, {}, {})


def transform_args_for_hash(*fargs, **fkwargs):
    inputs = [(None, arg) for arg in fargs]
    inputs.extend(sorted(fkwargs.items(), key = lambda x: x[0]))
    return tuple(inputs)
