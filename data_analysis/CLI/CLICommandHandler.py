import argparse
import os
import sys
from importlib import import_module
from pathlib import Path

sys.path.append(os.path.pardir)

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
        get_data_parser.add_argument('-e', '--exp', required=True, help='Experiment directory')
        get_data_parser.add_argument('-eids', '--exp_ids', nargs='*', required=True,
                                     help='Experiment IDs (that are identical to lowercase experiment classnames) to \
                                     get data from [example: "gl6 gl2_2 gl5"]')
        get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
        get_log_files_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment type')
        clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                            help='Clean experiment directory')
        clean_experiment_dir_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment type')
        clean_experiment_dir_parser.add_argument('--full', action='store_true', default=False,
                                                 help='Clean the entire directory')
        run_experiment_parser = subparsers.add_parser('run_experiment', aliases=["run-exp"], help='Run experiment')
        run_experiment_parser.add_argument('-eid', '--exp_id', type=str, required=True,
                                           help='Experiment ID (that is identical to lowercase experiment classname) \
                                           [example: "gl2", "gl5_2"]')
        run_experiment_parser.add_argument('-n', '--node', type=str, default="gl4",
                                           help='Node [default = "gl4", example: "gl2", "gl5"]')
        run_experiment_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment Directory')
        execute_parser = subparsers.add_parser('execute', aliases=['exec'], help='Execute a custom command')
        execute_parser.add_argument('-c', '--cmd', type=str, required=True, help='The command to execute')

        subparsers.add_parser('check_space', aliases=["space"], help='Check space of the cluster')
        check_dir_space = subparsers.add_parser('check_dir_space', aliases=["dir-space"],
                                                help='Check experiment directory space')
        check_dir_space.add_argument('-e', '--exp', required=True, type=str, help='Experiment Directory')

        create_experiment_parser = subparsers.add_parser('create_experiment', aliases=["create-exp"],
                                                         help='Create experiment')
        create_experiment_parser.add_argument('-d', '--dir', required=True, type=str, help='Experiment Directory')
        create_experiment_parser.add_argument('-c', '--cls', type=str, required=True,
                                              help='Experiment classname) [example: "Test", "GL2_3"]')

        subparsers.add_parser('sinfo', help='Slurm node information')
        subparsers.add_parser('squeue', help='Check slurm queue')
        subparsers.add_parser('sacct', help='Query slurm accountant to get experiment data')
        subparsers.add_parser('scancel', help='Cancel all running and pending jobs')

        args = parser.parse_args()
        if args.command in ['get_exp_data', "get-data"]:
            self.get_exp_data(ExperimentDir.value_to_enum(args.exp), args.exp_ids)
        elif args.command in ['check_space', "space"]:
            self.check_space()
        elif args.command in ['check_dir_space', "dir-space"]:
            self.check_dir_space(ExperimentDir.value_to_enum(args.exp))
        elif args.command == 'sinfo':
            self.client.execute_commands(["sinfo"])
        elif args.command == 'squeue':
            self.client.execute_commands(['squeue -o "%7A %50j %3t %N"'])
        elif args.command == 'sacct':
            self.client.execute_commands([
                "sacct -o jobid,jobname%60,cluster,Node%24,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,SystemCPU,UserCPU,AveCPU,elapsed,NCPUS"])
        elif args.command == 'scancel':
            self.client.execute_commands(["scancel -t R", "scancel -t PD", "squeue"])
        elif args.command in ['get_log_files', "get-logs"]:
            self.get_log_files(ExperimentDir.value_to_enum(args.exp))
        elif args.command in ['execute', 'exec']:
            self.client.execute_commands([args.cmd])
        elif args.command in ['clean_experiment_dir', "clean"]:
            self.clean_experiment_dir(ExperimentDir.value_to_enum(args.exp), args.full)
        elif args.command in ['create_experiment', "create-exp"]:
            self.create_experiment(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['run_experiment', "run-exp"]:
            exp_dir = ExperimentDir.value_to_enum(args.exp)
            if args.node == DEFAULT_NODE:
                CLICommandHandler(self.client).run_experiment(exp_dir, args.exp_id)
            else:
                node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(args.node))
                CLICommandHandler(node_client).run_experiment(exp_dir, args.exp_id)

    def get_exp_data(self, exp: 'ExperimentDir', experiment_ids):
        exp_dir = ExperimentDir.dir(exp)
        self.client.execute_commands(
            [f'cd {exp_dir}'] + [f'sh {PathRegistry.check_job_script(eid)}' for eid in experiment_ids])
        self.client.get_files(
            [ExperimentDir.dir(exp, PathRegistry.experiment_data_filename(eid)) for eid in experiment_ids],
            ExperimentDir.analysis_dir(exp, 'data'))

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

    def create_experiment(self, exp: 'ExperimentDir', cls: str):
        mode = EXPERIMENT_DIR_TO_MODE_MAP[exp]
        module_name = f"examples.domain.experiment.{mode.value.lower()}.{cls}"
        Exeriment_Class = getattr(import_module(module_name), cls)
        Exeriment_Class(ExperimentDir.host_dir(exp)).generate_create_job_script().generate_runner()
