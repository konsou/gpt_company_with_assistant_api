import atexit
import os
import random
import socket
import string

import docker
import docker.errors
import docker.models.containers
import docker.models.images
import docker.types
import paramiko

from workspace import Workspace
from workspace.base import CommandResult


def generate_random_chars(length: int) -> str:
    chars = string.ascii_lowercase + string.digits
    random_chars = "".join(random.choice(chars) for _ in range(length))
    return random_chars


def reserve_free_port() -> int:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    return tcp.getsockname()[1]


WORKSPACE_DIR = "./agent-workspace"
WORKSPACE_SSH_PRIVATE_KEY = "./ssh/workspace-ssh-key"
DOCKER_WORK_DIR = "/root/workspace"
DOCKER_IMAGE_NAME = "ai-agent-workspace"
DOCKER_CONTAINER_NAME = f"ai-agent-workspace-{generate_random_chars(5)}"
DOCKER_HOST_SSH_PORT = reserve_free_port()


class DockerWorkspace(Workspace):
    def __init__(self):
        super().__init__()

        print(f"Initialising Docker workspace...")
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        self._client = docker.from_env()
        try:
            self._image = self._client.images.get(DOCKER_IMAGE_NAME)
        except docker.errors.ImageNotFound:
            self._image = self._build_image()
        atexit.register(self.cleanup)
        self._container = self._run_container()
        self._ssh = self._connect_ssh()
        print(f"Initialisation complete")

    def run_command(self, command: str) -> CommandResult:
        print(f"Running command: {command}")
        stdin, stdout, stderr = self._ssh.exec_command(command)

        output = stdout.read().decode("utf-8") + stderr.read().decode("utf-8")

        print(f"Command output: {output}")
        return CommandResult(
            # TODO: return code
            status=0,
            content=output,
        )

    def cleanup(self):
        print(f"Stopping docker container {DOCKER_CONTAINER_NAME}...")
        self._ssh.close()
        self._container.stop()

    def _build_image(self) -> docker.models.images.Image:
        print(f"Building docker image {DOCKER_IMAGE_NAME}...")
        return self._client.images.build(path=".", tag=DOCKER_IMAGE_NAME)

    def _run_container(self) -> docker.models.containers.Container:
        print(f"Running docker container {DOCKER_CONTAINER_NAME}...")
        return self._client.containers.run(
            DOCKER_IMAGE_NAME,
            name=DOCKER_CONTAINER_NAME,
            detach=True,
            auto_remove=True,
            mounts=[
                docker.types.Mount(
                    source=os.path.abspath(WORKSPACE_DIR),
                    target=DOCKER_WORK_DIR,
                    type="bind",
                )
            ],
            ports={22: DOCKER_HOST_SSH_PORT},
        )

    def _connect_ssh(self):
        print(f"Starting shell inside docker container...")

        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the container via SSH
        ssh.connect(
            hostname="localhost",
            port=DOCKER_HOST_SSH_PORT,
            username="root",
            key_filename=WORKSPACE_SSH_PRIVATE_KEY,
        )

        return ssh


if __name__ == "__main__":
    ws = DockerWorkspace()
    input("ENTER")
    res = ws.run_command("pwd")
    res = ws.run_command("cd /")
    res = ws.run_command("pwd")
