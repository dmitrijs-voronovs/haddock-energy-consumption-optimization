from CLI.CLICommandHandler import CLICommandHandler
from CLI.CredentialManager import CredentialManager
from CLI.RemoteSSHClient import RemoteSSHClient


def main():
    client = RemoteSSHClient(*CredentialManager.get_credentials_for_node("gl4"))
    CLICommandHandler(client).execute_cli_command()


if __name__ == '__main__':
    main()
