import argparse
import os
import re
import sys
from importlib import import_module
from pathlib import Path

import pandas as pd

sys.path.append(os.path.pardir)

from examples.domain.experiment.Experiment import Experiment
from examples import PathRegistry
from .Constants import ExperimentDir, EXPERIMENT_DIR_TO_MODE_MAP
from .CredentialManager import CredentialManager, DEFAULT_NODE
from .RemoteSSHClient import RemoteSSHClient


class CLICommandHandler:
    def __init__(self, client):
        self.client: 'RemoteSSHClient' = client

    def execute_cli_command(self):
        parser = argparse.ArgumentParser(description='Remote SSH Client')
        subparsers = parser.add_subparsers(dest='command')
        get_data_parser = subparsers.add_parser('get_exp_data', aliases=["get-data"], help='Get experiment data')
        self.add_dir_arg(get_data_parser)
        get_data_parser.add_argument('-c', '--cls', nargs='*', required=True,
                                     help='Experiment classnames [example: "Test", "GL2_3"]')
        get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
        self.add_dir_arg(get_log_files_parser)
        clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                            help='Clean experiment directory')
        self.add_dir_arg(clean_experiment_dir_parser)
        clean_experiment_dir_parser.add_argument('--full', action='store_true', default=False,
                                                 help='Clean the entire directory')
        run_experiment_parser = subparsers.add_parser('run_experiment', aliases=["run-exp"], help='Run experiment')
        run_experiment_parser.add_argument('-n', '--node', type=str, required=True,
                                           help='Node [example: "gl2", "gl5"]')
        self.add_dir_arg(run_experiment_parser)
        self.add_cls_arg(run_experiment_parser)

        execute_parser = subparsers.add_parser('execute', aliases=['exec'], help='Execute a custom command')
        execute_parser.add_argument('cmd', nargs=argparse.REMAINDER, help='The command to execute')

        subparsers.add_parser('check_space', aliases=["space"], help='Check space of the cluster')
        check_dir_space = subparsers.add_parser('check_dir_space', aliases=["dir-space"],
                                                help='Check experiment directory space')
        self.add_dir_arg(check_dir_space)

        create_experiment_parser = subparsers.add_parser('create_experiment', aliases=["create-exp"],
                                                         help='Create experiment')
        self.add_dir_arg(create_experiment_parser)
        self.add_cls_arg(create_experiment_parser)

        get_info_data_parser = subparsers.add_parser('get_info_data', aliases=["get-info"],
                                                     help='Get experiment info data (consumed energy from perf module)')
        self.add_dir_arg(get_info_data_parser)
        self.add_cls_arg(get_info_data_parser)

        subparsers.add_parser('sinfo', help='Slurm node information')
        subparsers.add_parser('squeue', help='Check slurm queue')
        subparsers.add_parser('sacct', help='Query slurm accountant to get experiment data')
        subparsers.add_parser('scancel', help='Cancel all running and pending jobs')

        args = parser.parse_args()
        if args.command in ['get_exp_data', "get-data"]:
            self.get_exp_data(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['check_space', "space"]:
            self.check_space()
        elif args.command in ['check_dir_space', "dir-space"]:
            self.check_dir_space(ExperimentDir.value_to_enum(args.dir))
        elif args.command == 'sinfo':
            self.client.execute_commands(["sinfo"])
        elif args.command == 'squeue':
            self.client.execute_commands(['squeue -o "%7A %50j %3t %N"'])
        elif args.command == 'sacct':
            self.client.execute_commands([
                f"sacct -o {Experiment.get_sacct_output_format(main_fields_only=True)}"])
        elif args.command == 'scancel':
            self.client.execute_commands(["scancel -t R", "scancel -t PD", "squeue"])
        elif args.command in ['get_log_files', "get-logs"]:
            self.get_log_files(ExperimentDir.value_to_enum(args.dir))
        elif args.command in ['execute', 'exec']:
            self.client.execute_commands([' '.join(args.cmd)])
        elif args.command in ['clean_experiment_dir', "clean"]:
            self.clean_experiment_dir(ExperimentDir.value_to_enum(args.dir), args.full)
        elif args.command in ['create_experiment', "create-exp"]:
            self.create_experiment(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['get_info_data', "get-info"]:
            self.get_info_data(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['run_experiment', "run-exp"]:
            exp_dir = ExperimentDir.value_to_enum(args.dir)
            if args.node == DEFAULT_NODE:
                CLICommandHandler(self.client).run_experiment(exp_dir, args.cls)
            else:
                node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(args.node))
                CLICommandHandler(node_client).run_experiment(exp_dir, args.cls)

    def add_dir_arg(self, parser):
        parser.add_argument('-d', '--dir', type=str, required=True, help='Experiment directory')

    def add_cls_arg(self, parser):
        parser.add_argument('-c', '--cls', type=str, required=True,
                            help='Experiment classname [example: "Test", "GL2_3"]')

    def get_exp_data(self, exp: 'ExperimentDir', experiment_ids):
        exp_dir = ExperimentDir.dir(exp)
        self.client.execute_commands(
            [f'cd {exp_dir}'] + [f'sh {PathRegistry.check_job_script(eid)}' for eid in experiment_ids] + [
                f'sh {PathRegistry.check_job_script(eid, full=True)}' for eid in experiment_ids])
        self.client.get_files(
            [ExperimentDir.dir(exp, PathRegistry.experiment_data_filename(eid)) for eid in experiment_ids],
            ExperimentDir.analysis_dir(exp, 'data'))
        self.client.get_files(
            [ExperimentDir.dir(exp, PathRegistry.experiment_data_filename(eid, full=True)) for eid in experiment_ids],
            ExperimentDir.analysis_dir(exp, 'full', 'data'))

    def clean_experiment_dir(self, exp: 'ExperimentDir', full: bool):
        exp_dir = ExperimentDir.dir(exp)
        self.client.put_files([PathRegistry.clean_script()], exp_dir)
        print(full)
        if full:
            self.client.execute_commands(
                [f'cd {exp_dir}', 'rm -rf run.*', 'rm -rf *.info', 'rm -rf *.cfg', 'rm -rf slurm-*'])
        else:
            self.client.execute_commands([f'cd {exp_dir}', 'sh clean.sh'])

    def get_haddock_log_files(self, exp: 'ExperimentDir', subdir='runs'):
        exp_dir = ExperimentDir.dir(exp)
        all_directories = self.client.execute_commands([f'cd {exp_dir}',  # list directories that have pattern run.*
                                                        'ls -d run.*/', ]).splitlines()

        for directory in all_directories:
            directory = directory.strip("/")
            destination_dir = ExperimentDir.host_dir(exp, subdir, directory)

            if Path(destination_dir).exists():
                continue

            files = self.client.execute_commands(
                [f'cd {exp_dir}', f'cd {directory}',  # list all files-only no directories
                 'ls -p | grep -v /', ]).splitlines()
            files_abs_path = [f"{exp_dir}/{directory}/{file}" for file in files]
            print(files_abs_path)
            self.client.get_files(files_abs_path, destination_dir)

    def get_slurm_files(self, exp: 'ExperimentDir', subdir='slurm'):
        exp_dir = ExperimentDir.dir(exp)
        slurm_files = self.client.execute_commands([f'cd {exp_dir}', 'ls -p slurm-* | grep -v /', ]).splitlines()

        destination_dir = ExperimentDir.host_dir(exp, subdir)
        new_slurm_files = [f"{exp_dir}/{file}" for file in slurm_files if
                           not Path(f"{destination_dir}/{file}").exists()]

        self.client.get_files(new_slurm_files, destination_dir)

    def get_log_files(self, exp: 'ExperimentDir'):
        self.get_haddock_log_files(exp)
        self.get_slurm_files(exp)

    def check_space(self):
        self.client.execute_commands(["df -h"])

    def check_dir_space(self, exp: 'ExperimentDir'):
        exp_dir = ExperimentDir.dir(exp)
        self.client.execute_commands([f"cd {exp_dir}", "pwd", "du -h --max-depth=1 | sort -h"])

    # TODO: adjust later
    def prepare_experiment_dir(self, exp: 'ExperimentDir'):
        self.client.put_directory(ExperimentDir.host_dir(exp, 'data'), ExperimentDir.dir(exp, 'data'))
        self.client.put_directory(ExperimentDir.host_dir(exp, 'template'), ExperimentDir.dir(exp, 'template'))
        self.client.put_files(
            [ExperimentDir.host_dir(exp, PathRegistry.create_job_script())] + PathRegistry.info_scripts(),
            ExperimentDir.dir(exp))

    def run_experiment(self, exp: 'ExperimentDir', exp_id: str):
        self.prepare_experiment_dir(exp)

        exp_dir = ExperimentDir.dir(exp)

        create_jobs_script = PathRegistry.create_jobs_script(exp_id)
        run_experiment_script = PathRegistry.run_experiment_script(exp_id)
        scripts_for_transfer = [create_jobs_script, run_experiment_script]
        self.client.put_files([ExperimentDir.host_dir(exp, file) for file in scripts_for_transfer], exp_dir)

        self.client.execute_commands(
            [f"echo running experiment '{exp_id}' on $(hostname)", f"cd {exp_dir}", "pwd", f"sh {create_jobs_script}",
             "echo activate conda", "source $HOME/anaconda3/bin/activate", "conda activate haddock3",
             "echo run experiment", f"sh {run_experiment_script}", "sinfo"])

    def create_experiment_class(self, cls, mode):
        module_name = f"examples.domain.experiment.{mode.value.lower()}.{cls}"
        return getattr(import_module(module_name), cls)

    def create_experiment(self, exp: 'ExperimentDir', cls: str):
        mode = EXPERIMENT_DIR_TO_MODE_MAP[exp]
        Experiment_Class: 'Experiment' = self.create_experiment_class(cls, mode)(ExperimentDir.host_dir(exp))
        Experiment_Class.generate_create_job_script().generate_runner()

    @staticmethod
    def extract_numbers_from_file(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            numbers = re.findall(r"(?:\d+,?)+\.\d+", content)
            return [float(num.replace(',', '')) for num in numbers]

    def get_info_data(self, exp: 'ExperimentDir', cls: str):
        mode = EXPERIMENT_DIR_TO_MODE_MAP[exp]
        ExperimentClass: 'Experiment' = self.create_experiment_class(cls, mode)()

        files = [(cfg.name, ExperimentDir.host_dir(exp, 'runs', f"{cfg.run_dir}.info", "perf_stat.txt")) for cfg in
                 ExperimentClass.configs]
        job_data = []
        for job_name, file in files:
            try:
                power_energy_pkg, power_energy_ram, perf_elapsed = self.extract_numbers_from_file(file)
                job_data.append(
                    {"JobName": job_name, "power_energy_pkg": power_energy_pkg, "power_energy_ram": power_energy_ram,
                     "perf_elapsed": perf_elapsed})
            except Exception as e:
                print(f"Failed to extract data from file {file}", e)

        print(job_data)
        df = pd.DataFrame(job_data)
        os.makedirs(ExperimentDir.analysis_dir(exp, 'data', 'info'), exist_ok=True)
        df.to_csv(ExperimentDir.analysis_dir(exp, 'data', 'info', f'perf.{cls}.csv'), index=False)
