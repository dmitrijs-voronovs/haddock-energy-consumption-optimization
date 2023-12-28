from data_analysis.CLI.CLICommandHandler import CLICommandHandler
from data_analysis.CLI.CredentialManager import CredentialManager
from data_analysis.CLI.RemoteSSHClient import RemoteSSHClient


def main():
    client = RemoteSSHClient(*CredentialManager.get_credentials_for_node("gl4"))
    CLICommandHandler(client).execute_cli_command()


if __name__ == '__main__':
    main()
