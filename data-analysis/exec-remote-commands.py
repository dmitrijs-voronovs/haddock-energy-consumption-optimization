import argparse
from enum import Enum
from pathlib import Path
from typing import List

import paramiko
from dotenv import dotenv_values

HOST_EXPERIMENT_FOLDER = "../examples"


class ExperimentType(Enum):
    LOCAL = "exp-local"


SHARED_DIR = "/mnt/nfs_share/greenBeansHaddock"


def get_exp_dir(exp: 'ExperimentType'):
    return f"{SHARED_DIR}/{exp.value}"


LOCAL_EXP_DIR = get_exp_dir(ExperimentType.LOCAL)

env_values = dotenv_values("../.env")


class RemoteSSHClient:
    # Function to establish an SSH connection
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.__connect()

    def __connect(self):
        # Create an SSH client instance
        self.ssh_client = paramiko.SSHClient()

        # Automatically add the server's host key
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the server
            self.ssh_client.connect(self.server, username=self.username, password=self.password)
        except paramiko.AuthenticationException:
            print("Authentication failed, please check your credentials")

    def __del__(self):
        self.__close()

    def __close(self):
        self.ssh_client.close()

    def get_files(self, remote_files: List[str], destination_dir: str = "."):
        sftp_client = self.ssh_client.open_sftp()
        # Define the remote file paths
        # Download remote files to the current directory
        for remote_file in remote_files:
            filepath = Path(destination_dir) / Path(remote_file).name
            Path(filepath.parent).mkdir(parents=True, exist_ok=True)
            # Download the file
            sftp_client.get(remote_file, self.__get_filepath(filepath))
            print(f"Downloaded {filepath}")
        sftp_client.close()

    def put_files(self, local_files: List[str], destination_dir: str = SHARED_DIR):
        sftp_client = self.ssh_client.open_sftp()
        # Define the remote file paths
        # Download remote files to the current directory
        for local_file in local_files:
            filepath = Path(destination_dir) / Path(local_file).name

            # Download the file
            sftp_client.put(local_file, self.__get_filepath(filepath),
                            lambda x, y: print(f"Progress: {x / y * 100:.0f}%"))
            print(f"Uploaded {filepath}")
        sftp_client.close()

    def __get_filepath(self, filepath):
        return str(filepath).replace("\\", "/")

    def execute_commands(self, commands) -> str:
        command = " && ".join(commands)
        try:
            # Execute a command (replace this with your script execution)
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            # Read the output
            output = stdout.read().decode('utf-8')
            print(f"{command=}")
            print(output)
            return output
        except Exception as e:
            print(f"Error: {e}")
            return ""


def get_credentials_for_node(node) -> (str, str, str):
    server_ip = env_values.get(f"{node.upper()}-SERVER_IP")
    username = env_values.get("USERNAME")
    password = env_values.get("PASSWORD")
    return server_ip, username, password


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
            node_client = RemoteSSHClient(*get_credentials_for_node(node_name))
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


def main():
    client = RemoteSSHClient(*get_credentials_for_node("gl4"))
    CLICommandHandler(client).execute_cli_command()


if __name__ == '__main__':
    main()
