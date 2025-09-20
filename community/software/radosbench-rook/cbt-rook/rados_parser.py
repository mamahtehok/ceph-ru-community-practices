from __future__ import annotations
import json
import argparse
import fnmatch
import os
import yaml


def parse_files(jsons_list: list,yaml_list: list):



    def parse_jsons(_list: list) -> tuple[int,float]:

        sum_iops: int = 0
        sum_avg_lat: float = 0.0
        sum_bw: float = 0.0

        for _, _file in enumerate(_list):
            try:
                print(_file)
                with open(_file, 'r') as file:
                    content = file.read().strip()

                data = json.loads(content)

                average_iops = int(data.get("Average IOPS", 0))
                average_lat = float(data.get("Average Latency(s)", 0.0))
                bandwidth = float(data.get("Bandwidth (MB/sec)", 0.0))
                sum_iops += average_iops
                sum_avg_lat += average_lat
                sum_bw += bandwidth

                # Step 4: Return or print the values
                if args.details:
                    print(f"Average IOPS: {average_iops}")
                    print(f"Average Latensy(s): {average_lat}")
                    print(f"Bandwidth (MB/sec): {bandwidth}\n")

            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
            except (ValueError, KeyError) as e:
                print(f"Error extracting values: {e}")

        if args.comma:
            print(f"\n--------")
            print(f"Summary IOPS of all processes is {sum_iops}")
            print(f"Summary avg. lat(s) of all processes is {sum_avg_lat/len(_list):.3f}".replace('.',','))
            print(f"Summary bw(MB\\s) is {sum_bw:.3f}".replace('.',','))
            print(f"----------")
        else:
            print(f"\n--------")
            print(f"Summary IOPS of all processes is {sum_iops}")
            print(f"Summary avg. lat(s) of all processes is {sum_avg_lat/len(_list):.3f}")
            print(f"Summary bw(MB\\s) is {sum_bw:.3f}")
            print(f"----------")

    def parse_yaml(_list: list) -> list:
        for _file in _list:

            with open(_file, 'r') as file:
                content = file.read().strip()

            parsed_data = yaml.safe_load(content)
            print(f"\n+++++++Config details+++++++++")
            print(f"Benchmark: {parsed_data['cluster']['benchmark']}")
            print(f"Concurrent ops: {parsed_data['cluster']['concurrent_ops']}")
            print(f"Concurrent procs: {parsed_data['cluster']['concurrent_procs']}")
            print(f"Object size: {parsed_data['cluster']['op_size']} B")
            print(f"++++++++++++++++++++++++++++++\n")

    parse_jsons(jsons_list)
    parse_yaml(yaml_list)


def scan_dir(root_path):
    jsons = config = []
    iteration_sign = 0
    if not os.path.isdir(root_path):
        print(f"Directory '{root_path}' does not exist or is not a directory.")
        return

    # Get all top-level subdirectories in the results dir
    subdirs = sorted([entry for entry in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, entry))])
    # print(subdirs)

    # Get all the subdirs in 00000, 000001 etc. In other words, all of the op_sizes dirs
    for i in subdirs:
        iteration_sign = iteration_sign + 1  # This is just a sign for user to show that we are working on iteration of this number
        sub_path = os.path.join(root_path,i)
        sub_subdirs = sorted([entry for entry in os.listdir(sub_path) if os.path.isdir(os.path.join(sub_path, entry))])
        # print(sub_subdirs)
        print(f"\n ==============================Iteration {iteration_sign}================================== \n")

        if sub_subdirs:
            for dir_name in sub_subdirs:
                full_dir_path = os.path.join(sub_path, dir_name)  # Build full path
                # print(f"Full dir path is {full_dir_path}")
                jsons,config = list_files(full_dir_path)
                parse_files(jsons,config)
        else:
            print(f"No sub-directories found in {sub_path}")


def list_files(top_dir_path):

    # pattern_ls = ["json_output.*","benchmark_config.yaml"]
    json = "json_output.*"
    bench_conf = "benchmark_config.yaml"
    # print(f"Files in '{top_dir_path}' (and its subdirs):")
    # found_files = False
    config_ls = []
    json_ls = []

    # Recursively walk through the top_dir and all nested subdirs looking for json_output and benchmark.yaml
    for root, subdirs, files in os.walk(top_dir_path):
        for fn in files:
            # Here I create a list of jsons
            if fnmatch.fnmatch(fn, json):
                full_path = os.path.join(root, fn)  # Build full path
                json_ls.append(full_path)
            # And here benchmark
            if fnmatch.fnmatch(fn, bench_conf):
                full_path = os.path.join(root, fn)  # Build full path
                config_ls.append(full_path)
        # if json_ls is empty - no reason to proceed with processing
        if not json_ls:
            continue
        # print(f"json list is {json_ls}\n and config_list is {config_ls}")
        return json_ls,config_ls

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='parse results of radosbench tests')
    parser.add_argument('--dir', type=str, help='find files to parse',required=True)
    parser.add_argument('--details',action='store_true',help="Show results of all processes files")
    parser.add_argument('--comma',action='store_true',help="comma instead of dot in output")

    # Global to make it available outside of main. I know, this is shitcoding
    global args
    args = parser.parse_args()

    scan_dir(args.dir)
