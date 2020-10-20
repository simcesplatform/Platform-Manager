# -*- coding: utf-8 -*-

"""This module contains the functionality for starting Docker containers."""

import asyncio
import re
from typing import cast, Dict, List, Union

from aiodocker import Docker
from aiodocker.containers import DockerContainer

from tools.tools import EnvironmentVariableValue, FullLogger

LOGGER = FullLogger(__name__)


def get_container_name(container: DockerContainer) -> str:
    """Returns the name of the given Docker container."""
    # Use a hack to get the container name because the aiodocker does not make it otherwise available.
    return container._container.get("Names", [" "])[0][1:]  # pylint: disable=protected-access


class ContainerConfiguration:
    """Class for holding the parameters needed when starting a Docker container instance.
    Only parameters needed for starting containers for the simulation platform are included.
    """
    def __init__(self, container_name: str, docker_image: str, environment: Dict[str, EnvironmentVariableValue],
                 networks: Union[str, List[str]], volumes: Union[str, List[str]]):
        """
        Sets up the parameters for the Docker container configuration to the format required by aiodocker.
        - container_name:    the container name
        - docker_image:      the Docker image name including a tag
        - environment:       the environment variables and their values
        - networks:          the names of the Docker networks for the container
        - volumes:           the volume names and the target paths, format: <volume_name>:<target_path>[rw|ro]
        """
        self.__name = container_name
        self.__image = docker_image
        self.__environment = [
            "=".join([
                variable_name, str(variable_value)
            ])
            for variable_name, variable_value in environment.items()
        ]

        if isinstance(networks, str):
            self.__networks = [networks]
        else:
            self.__networks = networks

        if isinstance(volumes, str):
            self.__volumes = [volumes]
        else:
            self.__volumes = volumes

    @property
    def container_name(self) -> str:
        """The container name."""
        return self.__name

    @property
    def image(self) -> str:
        """The Docker image for the container."""
        return self.__image

    @property
    def environment(self) -> List[str]:
        """The environment variables for the Docker container."""
        return self.__environment

    @property
    def networks(self) -> List[str]:
        """The Docker networks for the Docker container."""
        return self.__networks

    @property
    def volumes(self) -> List[str]:
        """The Docker volumes for the Docker container."""
        return self.__volumes


class ContainerStarter:
    """Class for starting the Docker components for a simulation."""
    PREFIX_DIGITS = 2
    PREFIX_START = "Sim"

    def __init__(self):
        """Sets up the Docker client."""
        self.__container_prefix = "{:s}{{index:0{:d}d}}_".format(
            self.__class__.PREFIX_START, self.__class__.PREFIX_DIGITS)     # Sim{index:02d}_
        self.__prefix_pattern = re.compile("{:s}([0-9]{{{:d}}})_".format(
            self.__class__.PREFIX_START, self.__class__.PREFIX_DIGITS))    # Sim([0-9]{2})_

        self.__docker_client = Docker()
        self.__lock = asyncio.Lock()

    async def close(self):
        """Closes the Docker client connection."""
        await self.__docker_client.close()

    async def get_next_simulation_index(self) -> Union[int, None]:
        """
        Returns the next available index for the container name prefix for a new simulation.
        If all possible indexes are already in use, returns None.
        """
        running_containers = cast(List[DockerContainer], await self.__docker_client.containers.list())
        simulation_indexes = {
            int(get_container_name(container)[len(self.__class__.PREFIX_START):][:self.__class__.PREFIX_DIGITS])
            for container in running_containers
            if self.__prefix_pattern.match(get_container_name(container)) is not None
        }

        if simulation_indexes:
            index_limit = 10 ** self.__class__.PREFIX_DIGITS
            available_indexes = set(range(index_limit)) - simulation_indexes
            if available_indexes:
                return min(available_indexes)
            # no available simulation indexes available
            return None

        # no previous simulation containers found
        return 0

    async def start_simulation(self, simulation_configurations: List[ContainerConfiguration]) -> Union[List[str], None]:
        """
        Starts a Docker container with the given configuration parameters.
        Returns the names of the container objects representing the started containers.
        Returns None, if there was a problem starting any of the containers.
        """
        async with self.__lock:
            simulation_index = await self.get_next_simulation_index()
            if simulation_index is None:
                LOGGER.warning("No free simulation indexes.")
                return None

            simulation_containers = []
            container_names = []
            for container_configuration in simulation_configurations:
                full_container_name = (
                    self.__container_prefix.format(index=simulation_index) +
                    container_configuration.container_name)
                container_names.append(full_container_name)

                # The API specification for Docker Engine: https://docs.docker.com/engine/api/v1.40/
                LOGGER.debug("Creating container: {:s}".format(full_container_name))
                if container_configuration.networks:
                    first_network_name = container_configuration.networks[0]
                    first_network = {first_network_name: {}}
                else:
                    first_network = {}
                container = await self.__docker_client.containers.create_or_replace(
                    name=full_container_name,
                    config={
                        "Image": container_configuration.image,
                        "Env": container_configuration.environment,
                        "HostConfig": {
                            "Binds": container_configuration.volumes,
                            "AutoRemove": True
                        },
                        "NetworkingConfig": {
                            "EndpointsConfig": first_network
                        }
                    }
                )
                if not isinstance(container, DockerContainer):
                    LOGGER.warning("Failed to create container: {:s}".format(container_configuration.container_name))
                    return None

                # When creating a container, it can only be connected to one network.
                # The other networks have to be connected separately.
                for other_network_name in container_configuration.networks[1:]:
                    other_network = await self.__docker_client.networks.get(net_specs=other_network_name)
                    await other_network.connect(
                        config={
                            "Container": full_container_name,
                            "EndpointConfig": {}
                        }
                    )
                simulation_containers.append(container)

            for container_name, container in zip(container_names, simulation_containers):
                LOGGER.info("Starting container: {:s}".format(container_name))
                await container.start()

            return container_names

    async def stop_containers(self, container_names: List[str]):
        """Stops all the Docker containers in the given container name list."""
        # TODO: implement stop_containers

    async def stop_all_simulation_containers(self):
        """Stops all the Docker containers that have been started."""
        # TODO: implement stop_all_simulation_containers
