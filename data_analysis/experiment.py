from CLI.CLICommandHandler import CLICommandHandler
from CLI.CredentialManager import CredentialManager, DEFAULT_NODE
from CLI.RemoteSSHClient import RemoteSSHClient


def main():
    client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(DEFAULT_NODE))
    CLICommandHandler(client).execute_cli_command()


if __name__ == '__main__':
    main()
