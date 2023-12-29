from CLI.CLICommandHandler import CLICommandHandler
from CLI.CredentialManager import CredentialManager
from CLI.RemoteSSHClient import RemoteSSHClient

DEFAULT_NODE = "gl4"


def main():
    client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(DEFAULT_NODE))
    CLICommandHandler(client).execute_cli_command()


if __name__ == '__main__':
    main()
