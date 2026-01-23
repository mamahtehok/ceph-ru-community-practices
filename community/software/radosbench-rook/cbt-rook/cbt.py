#!/usr/bin/python3
import argparse
import collections
import logging
import sys

import settings
import benchmarkfactory
from cluster.ceph import Ceph
from log_support import setup_loggers

logger = logging.getLogger("cbt")
# Uncomment this if further debug detail (module, funcname) are needed
#FORMAT = "%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s():%(lineno)s] %(message)s"
#logging.basicConfig(format=FORMAT, force=True)
#logger.setLevel(logging.DEBUG)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Continuously run ceph tests.')
    parser.add_argument(
        '-a', '--archive',
        required=True,
        help='Directory where the results should be archived.',
    )

    parser.add_argument(
        '-c', '--conf',
        required=False,
        help='The ceph.conf file to use.',
    )

    parser.add_argument(
        'config_file',
        help='YAML config file.',
    )

    return parser.parse_args(args[1:])


def main(argv):
    setup_loggers()
    ctx = parse_args(argv)
    settings.initialize(ctx)

    global_init = collections.OrderedDict()
    archive_dir = settings.cluster.get('archive_dir')


    cluster = Ceph(settings.cluster)

    # Run the benchmarks
    return_code = 0
    try:
        for iteration in range(settings.cluster.get("iterations", 0)):
            print(f"\n\t\tRUNNNING ITERATION {iteration}")
            benchmarks = benchmarkfactory.get_all(archive_dir, cluster, iteration)
            for b in benchmarks:
                b.run(iteration)

    except:
        return_code = 1  # FAIL
        logger.exception("During tests")

    return return_code

if __name__ == '__main__':
    print(f"THIS IS FORK")
    exit(main(sys.argv))
