import logging
import hashlib
import os
import json
import yaml
import settings
import subprocess

logger = logging.getLogger('cbt')


class Benchmark(object):
    def __init__(self, archive_dir, cluster, config):
        self.acceptable = config.pop('acceptable', {})
        self.config = config
        self.cluster = cluster
        hashable = json.dumps(sorted(self.config.items())).encode()
        digest = hashlib.sha1(hashable).hexdigest()[:8]
        self.archive_dir = os.path.join(archive_dir,
                                        'results',
                                        '{:0>8}'.format(config.get('iteration')),
                                        'id-{}'.format(digest))
        # This would show several dirs if run continuously
        # logger.info("Results dir: %s", self.archive_dir )
        self.run_dir = os.path.join(settings.cluster.get('tmp_dir'),
                                    '{:0>8}'.format(config.get('iteration')),
                                    self.getclass())
        self.osd_ra = config.get('osd_ra', '0')
        self.cmd_path = ''
        self.valgrind = config.get('valgrind', None)
        self.cmd_path_full = ''
        self.log_iops = config.get('log_iops', True)
        self.log_bw = config.get('log_bw', True)
        self.log_lat = config.get('log_lat', True)

    def getclass(self):
        return self.__class__.__name__

    def run(self):
        subprocess.run(f"rm -rf {self.run_dir}",shell=True,text=True)
        self.cmd_path_full += self.cmd_path

        # Store the parameters of the test run
        config_file = os.path.join(self.archive_dir, 'benchmark_config.yaml')
        if not os.path.exists(self.archive_dir):
            # logger.info(f"Create dir {self.archive_dir}")
            os.makedirs(self.archive_dir)
        if not os.path.exists(config_file):
            config_dict = dict(cluster=self.config)
            with open(config_file, 'w') as fd:
                yaml.dump(config_dict, fd, default_flow_style=False)

    def exists(self):
        return False

    def __str__(self):
        return str(self.config)


