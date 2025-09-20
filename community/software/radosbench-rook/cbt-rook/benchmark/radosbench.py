import os
import logging
import json
import os
import subprocess
import shutil
import multiprocessing
import sys

from .benchmark import Benchmark

logger = logging.getLogger("cbt")


def fire_starter(cmd):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                check=False
            )
            # print(f"Subprocess completed with return code {result.returncode}")
            if result.returncode != 0:
                raise ValueError(f"Subprocess failed with code {result.returncode}")
        except Exception as e:
            print(f"Error running subprocess '{cmd}': {e}")
            raise


class Radosbench(Benchmark):

    def __init__(self, archive_dir, cluster, config):
        super(Radosbench, self).__init__(archive_dir, cluster, config)
        self.time = str(config.get('time', '300'))
        self.concurrent_procs = config.get('concurrent_procs', 1)
        self.concurrent_ops = config.get('concurrent_ops', 16)
        self.pool_per_proc = config.get('pool_per_proc', False)  # default behavior used to be True
        self.write_only = config.get('write_only', False)
        self.write_time = config.get('write_time', self.time)
        self.read_only = config.get('read_only', False)
        self.read_time = config.get('read_time', self.time)
        self.op_size = config.get('op_size', 4194304)
        self.object_set_id = config.get('object_set_id', '')
        self.run_dir = os.path.join(self.run_dir,
                                    'osd_ra-{:0>8}'.format(self.osd_ra),
                                    'op_size-{:0>8}'.format(self.op_size),
                                    'concurrent_ops-{:0>8}'.format(self.concurrent_ops))
        self.out_dir = self.archive_dir
        self.pool_profile = config.get('pool_profile', 'default')
        self.cmd_path = config.get('cmd_path', self.cluster.rados_cmd)
        self.pool = config.get('target_pool', 'rados-bench-cbt')
        self.readmode = config.get('readmode', 'seq')
        self.max_objects = config.get('max_objects', None)
        self.write_omap = config.get('write_omap', False)
        self.prefill_time = config.get('prefill_time', None)
        self.prefill_objects = config.get('prefill_objects', None)
        self.rebuild_every_test = config.get('rebuild_every_test',False)

    def run(self,iteration):
        super(Radosbench, self).run()

        do_prefill = self.prefill_time
        # sanity tests
        if self.read_only and self.write_only:
            logger.error('Both "read_only" and "write_only" are specified, '
                         'but they are mutually exclusive.')
            sys.exit(0)

            # return
        elif self.read_only and not do_prefill:
            logger.error(f"Please prefill with \"prefill_time"
                         f" option for a \"read_only\" test")
            sys.exit()
            # return

        # Shitcoding as I have no idea how to create EC profiles only once
        if iteration == 0:
            self.cluster.make_profiles()

        # Remake the pools
        if self.rebuild_every_test:
            self.mkpools()

        # Run prefill
        if do_prefill:
            self._run(mode='prefill', run_dir='prefill',
                      max_objects=self.prefill_objects,
                      runtime=self.prefill_time)
        # Run write test
        if self.write_only:
            self._run(mode='write', run_dir='write',
                      max_objects=self.max_objects,
                      runtime=self.write_time)

        # Run read test
        if self.read_only:
            self._run(mode=self.readmode, run_dir=self.readmode,
                      max_objects=None,
                      runtime=self.read_time)


    def _run(self, mode, run_dir, max_objects, runtime):

        if self.concurrent_ops:
            concurrent_ops_str = '--concurrent-ios %s' % self.concurrent_ops


        # Max Objects
        max_objects_str = ''
        if max_objects:
            max_objects_str = '--max-objects %s' % max_objects

        # Operation type
        op_type = mode
        if mode == 'prefill':
            logger.info(f"Prefilling objects")
            op_type = 'write'

        if op_type == 'write':
            op_size_str = '-b %s' % self.op_size
        else:
            op_size_str = ''

        # Write to OMAP
        write_omap_str = ''
        if self.write_omap:
            write_omap_str = '--write-omap'

        run_dir = os.path.join(self.run_dir, run_dir)
        # print(f"{run_dir}\n")
        os.makedirs(run_dir,exist_ok=True)

        # Run rados bench
        print(f"\nRunning radosbench {mode} test with bs {self.op_size} with consurrensy of {self.concurrent_procs} procs.")
        self.execute_test(max_objects_str,op_type,op_size_str,
                          write_omap_str,runtime,concurrent_ops_str)

    def execute_test(self,max_objects,op_type,
                    op_size,write_omap,runtime,
                    concurrent_ops_str):

        global commands, processes
        commands = []
        processes = []

        for i in range(self.concurrent_procs):
            out_file = '%s/output.%s' % (self.run_dir, i)
            objecter_log = '%s/objecter.%s.log' % (self.run_dir, i)
            pool_name = self.pool
            run_name = f"client-{i}"
            rados_bench_cmd_fmt = \
            "{cmd} -p {pool} bench {op_size_arg} {duration} " \
            "{op_type} {concurrent_ops_arg} {max_objects_arg} " \
            "{write_omap_arg} {run_name} --no-cleanup " \
            "2> {stderr} > {stdout}"
            rados_bench_cmd = rados_bench_cmd_fmt.format(
            cmd="rados",
            pool=pool_name,
            op_size_arg=op_size,
            duration=runtime,
            op_type=op_type,
            concurrent_ops_arg=concurrent_ops_str,
            max_objects_arg=max_objects,
            write_omap_arg=write_omap,
            run_name=run_name,
            stderr=objecter_log,
            stdout=out_file)
            # logger.debug(f"{rados_bench_cmd}")
            p = multiprocessing.Process(target=fire_starter,args=(rados_bench_cmd,))
            p.start()
            processes.append(p)
        logger.info(f"Waiting for all processes to complete")
        for p in processes:
            p.join()
        logger.info(f"All({self.concurrent_procs}) processes sucessfully completed")

        shutil.copytree(self.run_dir,self.out_dir,dirs_exist_ok=True)
        self.analyze(self.out_dir)


    def mkpools(self):
        self.cluster.rmpool(self.pool, self.pool_profile)
        self.cluster.mkpool(self.pool, self.pool_profile, 'radosbench')

    def parse(self, out_dir):
        for i in range(self.concurrent_procs):
            result = {}
            found = 0
            out_file = '%s/output.%s' % (out_dir, i )
            json_out_file = '%s/json_output.%s' % (out_dir, i)
            with open(out_file) as fd:
                for line in fd.readlines():
                    if found == 0:
                        if "Total time run" in line:
                            found = 1
                    if found == 1:
                        line = line.strip()
                        key, val = line.split(":")
                        result[key.strip()] = val.strip()
            with open(json_out_file, 'w') as json_fd:
                json.dump(result, json_fd)

    def analyze(self, out_dir):
        # logger.info('Converting results to json format.')
        self.parse(out_dir)

    def __str__(self):
        return "%s\n%s\n%s" % (self.run_dir, self.out_dir, super(Radosbench, self).__str__())
