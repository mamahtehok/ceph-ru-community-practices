import copy
import itertools

import settings
from benchmark.radosbench import Radosbench

def get_all(archive, cluster, iteration):
    for benchmark, config in sorted(settings.benchmarks.items()):
        default = {"benchmark": benchmark,
                   "iteration": iteration}
        for current in all_configs(config):
            current.update(default)
            yield get_object(archive, cluster, benchmark, current)


def all_configs(config):
    """
    return all parameter combinations for config
    config: dict - list of params
    iterate over all top-level lists in config
    """
    cycle_over_lists = []
    cycle_over_names = []
    default = {}

    for param, value in list(config.items()):
        # acceptable applies to benchmark as a whole, no need to it to
        # the set for permutation
        if param == 'acceptable':
            default[param] = value
        elif isinstance(value, list):
            cycle_over_lists.append(value)
            cycle_over_names.append(param)
        else:
            default[param] = value

    for permutation in itertools.product(*cycle_over_lists):
        current = copy.deepcopy(default)
        current.update(list(zip(cycle_over_names, permutation)))
        yield current

def get_object(archive, cluster, benchmark, bconfig):
    benchmarks = {
        'radosbench': Radosbench
        }
    try:
        return benchmarks[benchmark](archive, cluster, bconfig)
    except KeyError:
        return None
