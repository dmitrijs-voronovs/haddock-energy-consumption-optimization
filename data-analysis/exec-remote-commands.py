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

env_values = dotenv_values("../.env.gl2")


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
        command = "; ".join(commands)
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


def get_local_exp_data(client, experiments=None):
    if experiments is None:
        experiments = ["gl5"]

    client.execute_commands([
                                f'cd {LOCAL_EXP_DIR}',
                            ] + [f'sh check-local-exp-{experiment}.sh' for experiment in experiments])
    client.get_files([
        f"{LOCAL_EXP_DIR}/local-exp-{experiment}-data.txt" for experiment in experiments])


def clean_experiment_dir(client, exp: 'ExperimentType'):
    exp_dir = get_exp_dir(exp)
    client.put_files([
        f"{HOST_EXPERIMENT_FOLDER}/clean.sh",
    ], exp_dir)
    client.execute_commands([
        f'cd {exp_dir}',
        'sh clean.sh'
    ])


def get_haddock_log_files(client, exp: 'ExperimentType', subdir='runs'):
    exp_dir = get_exp_dir(exp)
    all_directories = client.execute_commands([
        f'cd {exp_dir}',
        #     list directories that have pattern run.*
        'ls -d run.*/',
    ]).splitlines()

    for directory in all_directories:
        directory = directory.strip("/")
        destination_dir = f"{HOST_EXPERIMENT_FOLDER}/{exp.value}/{subdir}/{directory}"

        if Path(destination_dir).exists():
            continue

        files = client.execute_commands([
            f'cd {exp_dir}',
            f'cd {directory}',
            # list all files-only no directories
            'ls -p | grep -v /',
        ]).splitlines()
        files_abs_path = [f"{exp_dir}/{directory}/{file}" for file in files]
        print(files_abs_path)
        client.get_files(files_abs_path, destination_dir)


def get_slurm_files(client, exp: 'ExperimentType', subdir='slurm'):
    exp_dir = get_exp_dir(exp)
    slurm_files = client.execute_commands([
        f'cd {exp_dir}',
        'ls -p slurm-* | grep -v /',
    ]).splitlines()

    destination_dir = f"{HOST_EXPERIMENT_FOLDER}/{exp.value}/{subdir}"
    new_slurm_files = [f"{exp_dir}/{file}" for file in slurm_files if not Path(f"{destination_dir}/{file}").exists()]

    client.get_files(new_slurm_files,
                     destination_dir)


def get_log_files(client, exp: 'ExperimentType'):
    get_haddock_log_files(client, exp)
    get_slurm_files(client, exp)


def check_space(client):
    client.execute_commands(["df -h"])


def check_folder_space(client):
    client.execute_commands([f"cd {LOCAL_EXP_DIR}", "pwd", "du -h --max-depth=1 | sort -h"])


def execute_cli_command(client):
    parser = argparse.ArgumentParser(description='Remote SSH Client')
    subparsers = parser.add_subparsers(dest='command')
    get_local_exp_data_parser = subparsers.add_parser('get_local_exp_data', aliases=["get-data"],
                                                      help='Get local experiment data')
    get_local_exp_data_parser.add_argument('-e', '--exp', nargs='*',
                                           help='Experiments to get data from, default ["gl6", "gl2_2", "gl5", "gl6_2"] ')
    check_space_parser = subparsers.add_parser('check_space', aliases=["space"], help='Check space')
    check_folders_space_parser = subparsers.add_parser('check_folder_space', aliases=["folder-space"],
                                                       help='Check folders space')
    get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
    get_log_files_parser.add_argument('-e', '--exp', type=str, help='Experiment type')
    clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                        help='Clean experiment directory')
    clean_experiment_dir_parser.add_argument('-e', '--exp', type=str, help='Experiment type')
    args = parser.parse_args()
    if args.command in ['get_local_exp_data', "get-data"]:
        get_local_exp_data(client, args.exp)
    elif args.command in ['check_space', "space"]:
        check_space(client)
    elif args.command in ['check_folder_space', "folder-space"]:
        check_folder_space(client)
    elif args.command in ['get_log_files', "get-logs"]:
        get_log_files(client, ExperimentType.LOCAL)
    elif args.command in ['clean_experiment_dir', "clean"]:
        clean_experiment_dir(client, ExperimentType.LOCAL)


def main():
    server_ip = env_values.get("SERVER_IP")
    username = env_values.get("USERNAME")
    password = env_values.get("PASSWORD")

    client = RemoteSSHClient(server_ip, username, password)
    execute_cli_command(client)


if __name__ == '__main__':
    main()
