from pathlib import Path
from typing import List

import paramiko
from dotenv import dotenv_values

# Load credentials from .env file
env_values = dotenv_values("../local.env")


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

    def copy_files(self, remote_files: List[str], destination_dir: str = "."):
        sftp_client = self.ssh_client.open_sftp()
        # Define the remote file paths
        # Download remote files to the current directory
        for remote_file in remote_files:
            filepath = Path(destination_dir) / Path(remote_file).name

            # Download the file
            sftp_client.get(remote_file, str(filepath))
            print(f"Downloaded {filepath}")

    def execute_commands(self, commands):
        for command in commands:
            # Execute a command (replace this with your script execution)
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            # Read the output
            output = stdout.read().decode('utf-8')
            print(f"{command=}, {output=}")
            print(output)


def get_local_exp_data(client):
    client.execute_commands([
        'cd /mnt/nfs_share/greenBeansHaddock/exp-local/',
        'sh check-local-exp-gl2.sh',
        'sh check-local-exp-gl6.sh',
    ])
    client.copy_files([
        "/mnt/nfs_share/greenBeansHaddock/exp-local/local-exp-gl2-data.txt",
        "/mnt/nfs_share/greenBeansHaddock/exp-local/local-exp-gl6-data.txt",
    ])


def main():
    server_ip = env_values.get("SERVER_IP")
    username = env_values.get("USERNAME")
    password = env_values.get("PASSWORD")

    client = RemoteSSHClient(server_ip, username, password)
    get_local_exp_data(client)


if __name__ == '__main__':
    main()
