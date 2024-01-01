import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.pardir)

from examples import NameRegistry
from .Constants import ExperimentFolder, HOST_EXPERIMENT_FOLDER
from .CredentialManager import CredentialManager, DEFAULT_NODE
from .RemoteSSHClient import RemoteSSHClient


class CLICommandHandler:
    def __init__(self, client):
        self.client: 'RemoteSSHClient' = client

    def execute_cli_command(self):
        parser = argparse.ArgumentParser(description='Remote SSH Client')
        subparsers = parser.add_subparsers(dest='command')
        get_local_exp_data_parser = subparsers.add_parser('get_local_exp_data', aliases=["get-data"],
                                                          help='Get local experiment data')
        get_local_exp_data_parser.add_argument('-e', '--exp', required=True, help='Experiment folder')
        get_local_exp_data_parser.add_argument('-eids', '--exp_ids', nargs='*', default='gl5',
                                               help='Experiments to get data from (i.e "gl6 gl2_2 gl5") ')
        get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
        get_log_files_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment type')
        clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                            help='Clean experiment directory')
        clean_experiment_dir_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment type')
        run_experiment_parser = subparsers.add_parser('run_experiment', aliases=["run-exp"], help='Run experiment')
        run_experiment_parser.add_argument('-eid', '--exp_id', type=str, required=True,
                                           help='Experiment ID (i.e. "gl2", "gl5_2"')
        run_experiment_parser.add_argument('-n', '--node', type=str, required=True, help='Node (i.e. "gl2", "gl5"')
        run_experiment_parser.add_argument('-e', '--exp', type=str, required=True, help='Experiment Folder')
        execute_parser = subparsers.add_parser('execute', aliases=['exec'], help='Execute a custom command')
        execute_parser.add_argument('-c', '--cmd', type=str, required=True, help='The command to execute')

        subparsers.add_parser('check_space', aliases=["space"], help='Check space')
        check_dir_space = subparsers.add_parser('check_dir_space', aliases=["dir-space"], help='Check folders space')
        check_dir_space.add_argument('-e', '--exp', required=True, type=str, help='Experiment Folder')

        subparsers.add_parser('sinfo', help='sinfo')
        subparsers.add_parser('squeue', help='squeue')
        subparsers.add_parser('scancel', help='scancel')

        args = parser.parse_args()
        if args.command in ['get_local_exp_data', "get-data"]:
            self.get_local_exp_data(ExperimentFolder.value_to_enum(args.exp), args.exp_ids)
        elif args.command in ['check_space', "space"]:
            self.check_space()
        elif args.command in ['check_dir_space', "dir-space"]:
            self.check_dir_space(ExperimentFolder.value_to_enum(args.exp))
        elif args.command == 'sinfo':
            self.client.execute_commands(["sinfo"])
        elif args.command == 'squeue':
            self.client.execute_commands(["squeue"])
        elif args.command == 'scancel':
            self.client.execute_commands(["scancel -t R", "scancel -t PD", "squeue"])
        elif args.command in ['get_log_files', "get-logs"]:
            self.get_log_files(ExperimentFolder.value_to_enum(args.exp))
        elif args.command in ['execute', 'exec']:
            self.client.execute_commands([args.cmd])
        elif args.command in ['clean_experiment_dir', "clean"]:
            self.clean_experiment_dir(ExperimentFolder.value_to_enum(args.exp))
        elif args.command in ['run_experiment', "run-exp"]:
            exp_dir = ExperimentFolder.value_to_enum(args.exp)
            if args.node == DEFAULT_NODE:
                CLICommandHandler(self.client).run_experiment(exp_dir, args.exp_id)
            else:
                node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(args.node))
                CLICommandHandler(node_client).run_experiment(exp_dir, args.exp_id)

    def get_local_exp_data(self, exp: 'ExperimentFolder', experiment_ids):
        exp_dir = ExperimentFolder.dir(exp)
        self.client.execute_commands(
            [f'cd {exp_dir}'] + [f'sh {NameRegistry.check_job_script(eid)}' for eid in experiment_ids])
        self.client.get_files(
            [ExperimentFolder.dir(exp, NameRegistry.experiment_data_filename(eid)) for eid in experiment_ids],
            ExperimentFolder.analysis_dir(exp, 'data'))

    def clean_experiment_dir(self, exp: 'ExperimentFolder'):
        exp_dir = ExperimentFolder.dir(exp)
        self.client.put_files([f"{HOST_EXPERIMENT_FOLDER}/clean.sh", ], exp_dir)
        self.client.execute_commands([f'cd {exp_dir}', 'sh clean.sh'])

    def get_haddock_log_files(self, exp: 'ExperimentFolder', subdir='runs'):
        exp_dir = ExperimentFolder.dir(exp)
        all_directories = self.client.execute_commands([f'cd {exp_dir}',  # list directories that have pattern run.*
                                                        'ls -d run.*/', ]).splitlines()

        for directory in all_directories:
            directory = directory.strip("/")
            destination_dir = ExperimentFolder.analysis_dir(exp, subdir, directory)

            if Path(destination_dir).exists():
                continue

            files = self.client.execute_commands(
                [f'cd {exp_dir}', f'cd {directory}',  # list all files-only no directories
                 'ls -p | grep -v /', ]).splitlines()
            files_abs_path = [f"{exp_dir}/{directory}/{file}" for file in files]
            print(files_abs_path)
            self.client.get_files(files_abs_path, destination_dir)

    def get_slurm_files(self, exp: 'ExperimentFolder', subdir='slurm'):
        exp_dir = ExperimentFolder.dir(exp)
        slurm_files = self.client.execute_commands([f'cd {exp_dir}', 'ls -p slurm-* | grep -v /', ]).splitlines()

        destination_dir = ExperimentFolder.analysis_dir(exp, subdir)
        new_slurm_files = [f"{exp_dir}/{file}" for file in slurm_files if
                           not Path(f"{destination_dir}/{file}").exists()]

        self.client.get_files(new_slurm_files, destination_dir)

    def get_log_files(self, exp: 'ExperimentFolder'):
        self.get_haddock_log_files(exp)
        self.get_slurm_files(exp)

    def check_space(self):
        self.client.execute_commands(["df -h"])

    def check_dir_space(self, exp: 'ExperimentFolder'):
        exp_dir = ExperimentFolder.dir(exp)
        self.client.execute_commands([f"cd {exp_dir}", "pwd", "du -h --max-depth=1 | sort -h"])

    # TODO: adjust later
    def prepare_experiment_dir(self, exp: 'ExperimentFolder'):
        self.client.put_directory(ExperimentFolder.analysis_dir(exp, 'data'), ExperimentFolder.dir(exp, 'data'))
        self.client.put_directory(ExperimentFolder.analysis_dir(exp, 'template'), ExperimentFolder.dir(exp, 'template'))
        self.client.put_files([ExperimentFolder.analysis_dir(exp, NameRegistry.create_job_script())],
                              ExperimentFolder.dir(exp))

    def run_experiment(self, exp: 'ExperimentFolder', exp_id: str):
        self.prepare_experiment_dir(exp)

        exp_dir = ExperimentFolder.dir(exp)

        create_jobs_script = NameRegistry.create_jobs_script(exp_id)
        run_experiment_script = NameRegistry.run_experiment_script(exp_id)
        scripts_for_transfer = [create_jobs_script, run_experiment_script]
        self.client.put_files([ExperimentFolder.analysis_dir(exp, file) for file in scripts_for_transfer], exp_dir)

        self.client.execute_commands(
            [f"echo running experiment '{exp_id}' on $(hostname)", f"cd {exp_dir}", "pwd", f"sh {create_jobs_script}",
             "echo activate conda", "source $HOME/anaconda3/bin/activate", "conda activate haddock3",
             "echo run experiment", f"sh {run_experiment_script}", "sinfo"])
