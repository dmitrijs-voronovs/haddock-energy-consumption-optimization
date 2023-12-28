from pathlib import Path
from typing import List

import paramiko

from .Constants import SHARED_DIR


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
