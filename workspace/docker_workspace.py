import os
import random
import string

import docker
import docker.errors
import docker.models.containers
import docker.models.images
import docker.types

from workspace import Workspace
from workspace.base import CommandResult


def generate_random_chars(length: int) -> str:
    chars = string.ascii_lowercase + string.digits
    random_chars = "".join(random.choice(chars) for _ in range(length))
    return random_chars


WORKSPACE_DIR = "./agent-workspace"
DOCKER_IMAGE_NAME = "ai-agent-workspace"
DOCKER_CONTAINER_NAME = f"ai-agent-workspace-{generate_random_chars(5)}"


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
        self._container = self._run_container()
        print(f"Initialisation complete")

    def run_command(self, command: str) -> CommandResult:
        raise NotImplementedError

    def cleanup(self):
        print(f"Stopping docker container")
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
                    target="/root/workspace",
                    type="bind",
                )
            ],
        )


if __name__ == "__main__":
    ws = DockerWorkspace()
    input("Press ENTER to continue")
    ws.cleanup()
