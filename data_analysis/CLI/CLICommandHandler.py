import argparse
from pathlib import Path

from .Constants import ExperimentType, LOCAL_EXP_DIR, get_exp_dir, HOST_EXPERIMENT_FOLDER
from .CredentialManager import CredentialManager
from .RemoteSSHClient import RemoteSSHClient


class CLICommandHandler:
    def __init__(self, client):
        self.client = client

    def execute_cli_command(self):
        parser = argparse.ArgumentParser(description='Remote SSH Client')
        subparsers = parser.add_subparsers(dest='command')
        get_local_exp_data_parser = subparsers.add_parser('get_local_exp_data', aliases=["get-data"],
                                                          help='Get local experiment data')
        get_local_exp_data_parser.add_argument('-e', '--exp', nargs='*',
                                               help='Experiments to get data from, default ["gl6", "gl2_2", "gl5", "gl6_2"] ')
        get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
        get_log_files_parser.add_argument('-e', '--exp', type=str, help='Experiment type')
        clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                            help='Clean experiment directory')
        clean_experiment_dir_parser.add_argument('-e', '--exp', type=str, help='Experiment type')
        run_experiment_parser = subparsers.add_parser('run_experiment', aliases=["run-exp"], help='Run experiment')
        run_experiment_parser.add_argument('-e', '--exp', type=str, help='Experiment ID (i.e. "gl2" or "gl5_2"')
        execute_parser = subparsers.add_parser('execute', help='Execute a custom command')
        execute_parser.add_argument('-c', '--cmd', type=str, required=True, help='The command to execute')

        subparsers.add_parser('check_space', aliases=["space"], help='Check space')
        subparsers.add_parser('check_folder_space', aliases=["dir-space"],
                              help='Check folders space')
        subparsers.add_parser('sinfo', help='sinfo')
        subparsers.add_parser('squeue', help='squeue')
        subparsers.add_parser('scancel', help='scancel')

        args = parser.parse_args()
        if args.command in ['get_local_exp_data', "get-data"]:
            self.get_local_exp_data(args.exp)
        elif args.command in ['check_space', "space"]:
            self.check_space()
        elif args.command in ['check_folder_space', "dir-space"]:
            self.check_folder_space()
        elif args.command == 'sinfo':
            self.client.execute_commands(["sinfo"])
        elif args.command == 'squeue':
            self.client.execute_commands(["squeue"])
        elif args.command == 'scancel':
            self.client.execute_commands(["scancel -t R", "scancel -t PD", "squeue"])
        elif args.command in ['get_log_files', "get-logs"]:
            self.get_log_files(ExperimentType.LOCAL)
        elif args.command == 'execute':
            self.client.execute_commands([args.cmd])
        elif args.command in ['clean_experiment_dir', "clean"]:
            self.clean_experiment_dir(ExperimentType.LOCAL)
        elif args.command in ['run_experiment', "run-exp"]:
            node_name = args.exp.split('_')[0]
            node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(node_name))
            CLICommandHandler(node_client).run_experiment(args.exp)

    def get_local_exp_data(self, experiments=None):
        if experiments is None:
            experiments = ["gl2_3", "gl5_2", "gl6_3"]

        self.client.execute_commands([
                                         f'cd {LOCAL_EXP_DIR}',
                                     ] + [f'sh check-local-exp-{experiment}.sh' for experiment in experiments])
        self.client.get_files([
            f"{LOCAL_EXP_DIR}/local-exp-{experiment}-data.txt" for experiment in experiments],
            f"{ExperimentType.LOCAL.value}/")

    def clean_experiment_dir(self, exp: 'ExperimentType'):
        exp_dir = get_exp_dir(exp)
        self.client.put_files([
            f"{HOST_EXPERIMENT_FOLDER}/clean.sh",
        ], exp_dir)
        self.client.execute_commands([
            f'cd {exp_dir}',
            'sh clean.sh'
        ])

    def get_haddock_log_files(self, exp: 'ExperimentType', subdir='runs'):
        exp_dir = get_exp_dir(exp)
        all_directories = self.client.execute_commands([
            f'cd {exp_dir}',
            #     list directories that have pattern run.*
            'ls -d run.*/',
        ]).splitlines()

        for directory in all_directories:
            directory = directory.strip("/")
            destination_dir = f"{HOST_EXPERIMENT_FOLDER}/{exp.value}/{subdir}/{directory}"

            if Path(destination_dir).exists():
                continue

            files = self.client.execute_commands([
                f'cd {exp_dir}',
                f'cd {directory}',
                # list all files-only no directories
                'ls -p | grep -v /',
            ]).splitlines()
            files_abs_path = [f"{exp_dir}/{directory}/{file}" for file in files]
            print(files_abs_path)
            self.client.get_files(files_abs_path, destination_dir)

    def get_slurm_files(self, exp: 'ExperimentType', subdir='slurm'):
        exp_dir = get_exp_dir(exp)
        slurm_files = self.client.execute_commands([
            f'cd {exp_dir}',
            'ls -p slurm-* | grep -v /',
        ]).splitlines()

        destination_dir = f"{HOST_EXPERIMENT_FOLDER}/{exp.value}/{subdir}"
        new_slurm_files = [f"{exp_dir}/{file}" for file in slurm_files if
                           not Path(f"{destination_dir}/{file}").exists()]

        self.client.get_files(new_slurm_files,
                              destination_dir)

    def get_log_files(self, exp: 'ExperimentType'):
        self.get_haddock_log_files(exp)
        self.get_slurm_files(exp)

    def check_space(self):
        self.client.execute_commands(["df -h"])

    def check_folder_space(self):
        self.client.execute_commands([f"cd {LOCAL_EXP_DIR}", "pwd", "du -h --max-depth=1 | sort -h"])

    # TODO: adjust later
    def prepare_experiment_dir(self, exp: 'ExperimentType'):
        exp_dir = get_exp_dir(exp)
        template_folder = f"{exp_dir}/template"
        # get all host files under template folder
        files = Path(template_folder).glob("**/*")

        self.client.put_files([
            f"{HOST_EXPERIMENT_FOLDER}/{exp.value}/",
        ], template_folder)

    def run_experiment(self, exp_id: str):
        # prepare_experiment_dir(client, ExperimentType.LOCAL)

        exp_host_folder = f"{HOST_EXPERIMENT_FOLDER}/{ExperimentType.LOCAL.value}"
        exp_folder = get_exp_dir(ExperimentType.LOCAL)

        create_jobs_script = f"all.create-local-jobs.{exp_id}.sh"
        run_experiment_script = f"run-local-exp-{exp_id}.sh"
        self.client.put_files(
            [f"{exp_host_folder}/{file}" for file in
             ["create-local-job.sh", create_jobs_script, run_experiment_script]],
            exp_folder)

        self.client.execute_commands([
            f"echo running experiment '{exp_id}' on $(hostname)",
            f"cd {exp_folder}",
            f"sh {create_jobs_script}",
            "sleep 2",
            "echo activate conda",
            "source $HOME/anaconda3/bin/activate",
            "conda activate haddock3",
            "echo run experiment",
            f"sh {run_experiment_script}",
            "sinfo"
        ])
