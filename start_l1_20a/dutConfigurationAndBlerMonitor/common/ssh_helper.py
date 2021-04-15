from paramiko import SSHClient
from paramiko import WarningPolicy
from paramiko import ssh_exception
import logging


logger = logging.getLogger(__name__)


class SSHHelper:

    def __init__(self, host: str, username: str, password: str):
        self.master_ip = host
        self.master_username = username
        self.master_password = password
        self.ssh_client = None

    def create_ssh(self):
        logger.info(f'SSH client is created with ip {self.master_ip}, '
                    f'username {self.master_username} and password {self.master_password}')
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(WarningPolicy())
        try:
            self.ssh_client.connect(
                self.master_ip,
                22,
                username=self.master_username,
                password=self.master_password,
                timeout=20,
                allow_agent=False,
                look_for_keys=False
            )
        except ssh_exception.AuthenticationException:
            self.ssh_client.get_transport().auth_none(self.master_username)

    def send(self, command: str):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdout.channel.recv_exit_status()
        response = ''.join(stdout.readlines())
        response = response.strip()
        logger.info(f'Response is {response} after sending {command}')

    def release(self):
        self.ssh_client.close()
        del self.ssh_client
        logger.info('SSH client closes')

