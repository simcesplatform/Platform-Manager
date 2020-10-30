# -*- coding: utf-8 -*-

"""This module contains the Platform Manager code that handles the starting of the simulation components for
   a simulation using the simulation platform.
"""

import asyncio
import dataclasses
import json
import logging
from typing import cast, Any, Dict, List

import yaml

from platform_manager.docker_runner import ContainerConfiguration, ContainerStarter
from tools.clients import RabbitmqClient, default_env_variable_definitions as default_rabbitmq_definitions
from tools.components import SIMULATION_ID, SIMULATION_COMPONENT_NAME, SIMULATION_STATE_MESSAGE_TOPIC, \
                             SIMULATION_EPOCH_MESSAGE_TOPIC, SIMULATION_STATUS_MESSAGE_TOPIC, \
                             SIMULATION_ERROR_MESSAGE_TOPIC
from tools.datetime_tools import get_utcnow_in_milliseconds, to_iso_format_datetime_string
from tools.db_clients import default_env_variable_definitions as default_mongodb_definitions
from tools.tools import FullLogger, load_environmental_variables, EnvironmentVariable, EnvironmentVariableValue, \
                        SIMULATION_LOG_LEVEL, SIMULATION_LOG_FILE, SIMULATION_LOG_FORMAT

LOGGER = FullLogger(__name__)

TIMEOUT = 5.0

# Names for environmental variables
RABBITMQ_EXCHANGE = "RABBITMQ_EXCHANGE"
RABBITMQ_EXCHANGE_AUTODELETE = "RABBITMQ_EXCHANGE_AUTODELETE"
RABBITMQ_EXCHANGE_DURABLE = "RABBITMQ_EXCHANGE_DURABLE"
RABBITMQ_EXCHANGE_PREFIX = "RABBITMQ_EXCHANGE_PREFIX"
MONGODB_APPNAME = "MONGODB_APPNAME"

SIMULATION_NAME = "SIMULATION_NAME"
SIMULATION_DESCRIPTION = "SIMULATION_DESCRIPTION"
SIMULATION_MANAGER_NAME = "SIMULATION_MANAGER_NAME"
SIMULATION_COMPONENTS = "SIMULATION_COMPONENTS"
SIMULATION_INITIAL_START_TIME = "SIMULATION_INITIAL_START_TIME"
SIMULATION_EPOCH_LENGTH = "SIMULATION_EPOCH_LENGTH"
SIMULATION_MAX_EPOCHS = "SIMULATION_MAX_EPOCHS"
SIMULATION_EPOCH_TIMER_INTERVAL = "SIMULATION_EPOCH_TIMER_INTERVAL"
SIMULATION_MAX_EPOCH_RESENDS = "SIMULATION_MAX_EPOCH_RESENDS"

SIMULATION_MANAGER_IMAGE = "SIMULATION_MANAGER_IMAGE"
SIMULATION_LOGWRITER_IMAGE = "SIMULATION_LOGWRITER_IMAGE"
SIMULATION_DOCKER_COMPONENTS = "SIMULATION_DOCKER_COMPONENTS"
SIMULATION_STATIC_COMPONENTS = "SIMULATION_STATIC_COMPONENTS"

MESSAGE_BUFFER_MAX_DOCUMENTS = "MESSAGE_BUFFER_MAX_DOCUMENTS"
MESSAGE_BUFFER_MAX_INTERVAL = "MESSAGE_BUFFER_MAX_INTERVAL"

DOCKER_NETWORK_MONGODB = "DOCKER_NETWORK_MONGODB"
DOCKER_NETWORK_RABBITMQ = "DOCKER_NETWORK_RABBITMQ"
DOCKER_NETWORK_PLATFORM = "DOCKER_NETWORK_PLATFORM"
DOCKER_VOLUME_NAME_RESOURCES = "DOCKER_VOLUME_NAME_RESOURCES"
DOCKER_VOLUME_NAME_LOGS = "DOCKER_VOLUME_NAME_LOGS"
DOCKER_VOLUME_TARGET_RESOURCES = "DOCKER_VOLUME_TARGET_RESOURCES"
DOCKET_VOLUME_TARGET_LOGS = "DOCKET_VOLUME_TARGET_LOGS"

# The main attributes in simulation configuration file
SIMULATION = "simulation"
COMPONENTS = "components"

# The overall simulation attributes in simulation configuration file
NAME = "name"
DESCRIPTION = "description"
START_TIME = "start_time"
EPOCH_LENGTH = "epoch_length"
MAX_EPOCHS = "max_epochs"

# The component specific attributes in simulation configuration file
DUPLICATION_COUNT = "duplication_count"


@dataclasses.dataclass
class ImageName:
    """Dataclass for holding Docker image names with including tags."""
    image_name: str
    image_tag: str = "latest"

    @property
    def full_name(self) -> str:
        """The full Docker image name including the tag."""
        return ":".join([self.image_name, self.image_tag])


class PlatformEnvironment:
    """Class for holding the values for non-simulation specific environment variables."""
    def __init__(self):
        """Loads the environmental variables that are used in the simulation components."""
        # TODO: add some checks for the parameters

        # setup the RabbitMQ parameters for the simulation specific exchange
        rabbitmq_env_variables = load_environmental_variables(*default_rabbitmq_definitions())
        # the exchange name is decided when starting a new simulation
        rabbitmq_env_variables.pop(RABBITMQ_EXCHANGE, None)
        self.__rabbitmq = {
            **rabbitmq_env_variables,
            RABBITMQ_EXCHANGE_AUTODELETE: True,
            RABBITMQ_EXCHANGE_DURABLE: False
        }
        self.__rabbitmq_exchange_prefix = cast(
            str, EnvironmentVariable(RABBITMQ_EXCHANGE_PREFIX, str, "procem.").value)

        # setup the MongoDB parameters for components needing database access
        self.__mongodb = load_environmental_variables(*default_mongodb_definitions())

        # setup the common parameters used by all simulation components
        self.__common = load_environmental_variables(
            (SIMULATION_LOG_LEVEL, int, logging.INFO),
            (SIMULATION_LOG_FILE, str),
            (SIMULATION_LOG_FORMAT, str),
            (SIMULATION_STATE_MESSAGE_TOPIC, str, "SimState"),
            (SIMULATION_EPOCH_MESSAGE_TOPIC, str, "Epoch"),
            (SIMULATION_STATUS_MESSAGE_TOPIC, str, "Status"),
            (SIMULATION_ERROR_MESSAGE_TOPIC, str, "Error")
        )

        self.__simulation_manager_image = ImageName(
            *cast(str, EnvironmentVariable(SIMULATION_MANAGER_IMAGE, str, "").value).split(":")
        )
        self.__logwriter_image = ImageName(
            *cast(str, EnvironmentVariable(SIMULATION_LOGWRITER_IMAGE, str, "").value).split(":")
        )
        self.__dynamic_component_types = {
            component_type: ImageName(*image_name_parts)
            for component_type, *image_name_parts in [
                dynamic_component_type.split(":")
                for dynamic_component_type in cast(
                    str, EnvironmentVariable(SIMULATION_DOCKER_COMPONENTS, str, "").value).split(",")
            ]
        }
        self.__static_component_types = cast(
            str, EnvironmentVariable(SIMULATION_STATIC_COMPONENTS, str, "").value).split(",")

        # setup the simulation manager specific parameters
        self.__manager = load_environmental_variables(
            (SIMULATION_MANAGER_NAME, str),
            (SIMULATION_EPOCH_TIMER_INTERVAL, float, 30.0),
            (SIMULATION_MAX_EPOCH_RESENDS, int, 5),
        )

        # setup the log writer specific parameters
        self.__logwriter = load_environmental_variables(
            (MESSAGE_BUFFER_MAX_DOCUMENTS, int, 10),
            (MESSAGE_BUFFER_MAX_INTERVAL, float, 5.0)
        )

        self.__docker = load_environmental_variables(
            (DOCKER_NETWORK_MONGODB, str),
            (DOCKER_NETWORK_RABBITMQ, str),
            (DOCKER_NETWORK_PLATFORM, str),
            (DOCKER_VOLUME_NAME_RESOURCES, str),
            (DOCKER_VOLUME_NAME_LOGS, str),
            (DOCKER_VOLUME_TARGET_RESOURCES, str),
            (DOCKET_VOLUME_TARGET_LOGS, str)
        )

    def get_dynamic_components(self) -> Dict[str, str]:
        """Returns the supported dynamic simulation components and their full Docker image names."""
        return {
            component_type: image_name.full_name
            for component_type, image_name in self.__dynamic_component_types.items()
        }

    def get_static_components(self) -> List[str]:
        """Returns a list of the supported static simulation component types."""
        return self.__static_component_types

    def get_manager_image(self) -> str:
        """Returns the full Docker image name for the Simulation Manager."""
        return self.__simulation_manager_image.full_name

    def get_logwriter_image(self) -> str:
        """Returns the full Docker image name for the Log Writer."""
        return self.__logwriter_image.full_name

    def get_rabbitmq_parameters(self, simulation_id: str) -> Dict[str, EnvironmentVariableValue]:
        """The simulation specific parameters for a RabbitMQ connection."""
        return {
            **self.__rabbitmq,
            RABBITMQ_EXCHANGE: self.get_simulation_exchange_name(simulation_id)
        }

    def get_manager_parameters(self, simulation_id: str) -> Dict[str, EnvironmentVariableValue]:
        """Returns the environment variables for simulation manager.
           Does not include the parameters set in the simulation configuration file."""
        return {
            **self.get_rabbitmq_parameters(simulation_id),
            **self.__common,
            **self.__manager,
            SIMULATION_ID: simulation_id,
            SIMULATION_LOG_FILE: self.get_component_log_filename(cast(str, self.__manager[SIMULATION_MANAGER_NAME]))
        }

    def get_logwriter_parameters(self, simulation_id: str) -> Dict[str, EnvironmentVariableValue]:
        """Returns the environment variables for log writer."""
        return {
            **self.get_rabbitmq_parameters(simulation_id),
            **self.__mongodb,
            **self.__common,
            **self.__logwriter,
            SIMULATION_ID: simulation_id,
            SIMULATION_LOG_FILE: self.get_component_log_filename(cast(str, self.__mongodb[MONGODB_APPNAME]))
        }

    def get_component_parameters(self, simulation_id: str, component_name: str) -> Dict[str, EnvironmentVariableValue]:
        """Returns the environment variables for a normal simulation component with the given component name.
           Does not include the parameters set in the simulation configuration file."""
        return {
            **self.get_rabbitmq_parameters(simulation_id),
            **self.__common,
            SIMULATION_ID: simulation_id,
            SIMULATION_COMPONENT_NAME: component_name,
            SIMULATION_LOG_FILE: self.get_component_log_filename(component_name)
        }

    def get_simulation_exchange_name(self, simulation_id: str) -> str:
        """Returns the name for the simulation specific exchange."""
        return (
            self.__rabbitmq_exchange_prefix +
            simulation_id.replace("-", "").replace(":", "").replace("Z", "").replace("T", "-").replace(".", "-")
        )

    def get_component_log_filename(self, component_name: str) -> str:
        """Returns the log filename for the given component."""
        filename_addition = "_" + component_name
        main_log_filename = cast(str, self.__common[SIMULATION_LOG_FILE])
        identifier_start = main_log_filename.rfind(".")

        if identifier_start == -1:
            return main_log_filename + filename_addition
        return main_log_filename[:identifier_start] + filename_addition + main_log_filename[identifier_start:]

    def get_docker_networks(self, rabbitmq: bool = True, mongodb: bool = False) -> List[str]:
        """Returns the names of the asked Docker networks."""
        docker_networks = [cast(str, self.__docker[DOCKER_NETWORK_PLATFORM])]
        if rabbitmq and self.__docker[DOCKER_NETWORK_RABBITMQ]:
            docker_networks.append(cast(str, self.__docker[DOCKER_NETWORK_RABBITMQ]))
        if mongodb and self.__docker[DOCKER_NETWORK_MONGODB]:
            docker_networks.append(cast(str, self.__docker[DOCKER_NETWORK_MONGODB]))
        return docker_networks

    def get_docker_volumes(self, resources: bool = True, logs: bool = True) -> List[str]:
        """Returns the binding of the Docker volumes.
           Resources volume is used for static files and logs volume is used for log output.
           The format for the binding values are: <volume_name>:<folder_name>[:<rw|ro>]
        """
        docker_volumes = []
        if resources and self.__docker[DOCKER_VOLUME_NAME_RESOURCES]:
            docker_volumes.append(":".join([
                cast(str, self.__docker[DOCKER_VOLUME_NAME_RESOURCES]),
                cast(str, self.__docker[DOCKER_VOLUME_TARGET_RESOURCES])
            ]))
        if logs and self.__docker[DOCKER_VOLUME_NAME_LOGS]:
            docker_volumes.append(":".join([
                cast(str, self.__docker[DOCKER_VOLUME_NAME_LOGS]),
                cast(str, self.__docker[DOCKET_VOLUME_TARGET_LOGS])
            ]))
        return docker_volumes


class PlatformManager:
    """PlatformManager handlers the starting of new simulations for the simulation platform."""
    def __init__(self):
        # Message bus client for sending messages to the management exchange.
        self.__rabbitmq_client = RabbitmqClient()

        # Load the environment variables.
        self.__platform_environment = PlatformEnvironment()

        # Open the Docker Engine connection.
        self.__container_starter = ContainerStarter()

        self.__is_stopped = False

    @property
    def is_stopped(self) -> bool:
        """Returns True, if the platform manager is stopped."""
        return self.__is_stopped

    async def stop(self):
        """Closes the connections to the RabbitMQ client and to the Docker Engine."""
        LOGGER.info("Stopping the platform manager.")
        await self.__rabbitmq_client.close()
        await self.__container_starter.close()
        self.__is_stopped = True

    async def start_simulation(self, simulation_configuration_file: str) -> bool:
        """Starts a new simulation using the given simulation configuration file."""
        # TODO: divide this massive function to multiple parts
        if self.is_stopped:
            return False

        with open(simulation_configuration_file, mode="r", encoding="utf-8") as configuration_yaml_file:
            simulation_configuration = yaml.safe_load(configuration_yaml_file)

        # TODO: add checking of simulation parameters

        simulation_id = get_utcnow_in_milliseconds()
        simulation_component_names = []
        simulation_component_settings = []
        for component_type, component_instances in simulation_configuration[COMPONENTS].items():
            if (component_type not in self.__platform_environment.get_dynamic_components() and
                    component_type not in self.__platform_environment.get_static_components()):
                LOGGER.error("Unknown component type, {:s}, found in the configuration file".format(component_type))
                return False
            elif component_type not in self.__platform_environment.get_dynamic_components():
                # Starting simulation runs with static component types is handled by Start message.
                continue

            for component_name, component_parameters in component_instances.items():
                component_count = int(component_parameters.get(DUPLICATION_COUNT, 1))
                component_parameters.pop(DUPLICATION_COUNT, None)

                for index in range(1, component_count + 1):
                    if component_count == 1:
                        full_component_name = component_name
                    else:
                        full_component_name = "_".join([component_name, str(index)])

                    component_specific_environment = {
                        **self.__platform_environment.get_component_parameters(
                            simulation_id, full_component_name),
                        **component_parameters
                    }
                    simulation_component_names.append(full_component_name)
                    simulation_component_settings.append(ContainerConfiguration(
                        container_name=full_component_name,
                        docker_image=self.__platform_environment.get_dynamic_components()[component_type],
                        environment=component_specific_environment,
                        networks=self.__platform_environment.get_docker_networks(),
                        volumes=self.__platform_environment.get_docker_volumes()
                    ))

        simulation_start_time = to_iso_format_datetime_string(simulation_configuration[SIMULATION][START_TIME])
        if simulation_start_time is None:
            LOGGER.error("Invalid simulation start time: {:s}".format(simulation_start_time))
            return False
        simulation_name = simulation_configuration[SIMULATION][NAME]
        manager_environment = {
            **self.__platform_environment.get_manager_parameters(simulation_id),
            SIMULATION_NAME: simulation_name,
            SIMULATION_DESCRIPTION: simulation_configuration[SIMULATION][DESCRIPTION],
            SIMULATION_COMPONENTS: ",".join(simulation_component_names),
            SIMULATION_INITIAL_START_TIME: simulation_start_time,
            SIMULATION_EPOCH_LENGTH: simulation_configuration[SIMULATION][EPOCH_LENGTH],
            SIMULATION_MAX_EPOCHS: simulation_configuration[SIMULATION][MAX_EPOCHS],
        }
        manager_settings = ContainerConfiguration(
            container_name=manager_environment[SIMULATION_MANAGER_NAME],
            docker_image=self.__platform_environment.get_manager_image(),
            environment=manager_environment,
            networks=self.__platform_environment.get_docker_networks(),
            volumes=self.__platform_environment.get_docker_volumes(resources=False)
        )

        logwriter_environment = self.__platform_environment.get_logwriter_parameters(simulation_id)
        logwriter_settings = ContainerConfiguration(
            container_name=cast(str, logwriter_environment[MONGODB_APPNAME]),
            docker_image=self.__platform_environment.get_logwriter_image(),
            environment=logwriter_environment,
            networks=self.__platform_environment.get_docker_networks(mongodb=True),
            volumes=self.__platform_environment.get_docker_volumes(resources=False)
        )

        all_settings = [logwriter_settings] + simulation_component_settings + [manager_settings]

        LOGGER.info("Starting the containers for simulation: '{:s}' with id: {:s}".format(
            simulation_name, simulation_id))
        container_names = await self.__container_starter.start_simulation(all_settings)

        if container_names is None:
            LOGGER.error("A problem starting the simulation.")
            return False

        await self.send_start_message(simulation_id, simulation_configuration)
        LOGGER.info("Start message for simulation '{:s}' sent to management exchange.".format(simulation_name))

        manager_container_name = container_names[-1]
        identifier_start_index = len(ContainerStarter.PREFIX_START)
        identifier_end_index = identifier_start_index + ContainerStarter.PREFIX_DIGITS
        simulation_identifier = manager_container_name[identifier_start_index:identifier_end_index]
        LOGGER.info("Simulation '{:s}' started successfully using id: {:s}".format(simulation_name, simulation_id))
        LOGGER.info("Follow the simulation by using the command: " +
                    "source follow_simulation.sh {:s}".format(simulation_identifier))
        # LOGGER.info("Follow the simulation through the simulation manager by using the command:\n" +
        #             "docker logs --follow {:s}".format(manager_container_name))

        return True

    async def send_start_message(self, simulation_id: str, simulation_configuration: Dict[str, Any]):
        """Sends a start message using the management exchange."""
        # TODO: add support for Start messages in simulation-tools
        start_message = {
            "Timestamp": get_utcnow_in_milliseconds(),
            "SimulationId": simulation_id,
            "SimulationSpecificExchange": self.__platform_environment.get_simulation_exchange_name(simulation_id),
            "SimulationName": simulation_configuration[SIMULATION][NAME],
            "SimulationDescription": simulation_configuration[SIMULATION][DESCRIPTION]
        }
        # TODO: add checking of configuration parameters, i.e. don't trust the user
        for component_type, component_instances in simulation_configuration.get(COMPONENTS, {}).items():
            if component_type in self.__platform_environment.get_static_components():
                start_message[component_type] = {}
                for component_instance, component_parameters in component_instances.items():
                    if DUPLICATION_COUNT in component_parameters:
                        # NOTE: at least for now, duplication_count, is not considered for static components
                        component_parameters.pop(DUPLICATION_COUNT, None)
                    start_message[component_type][component_instance] = component_parameters

        start_message_bytes = bytes(json.dumps(start_message), encoding="utf-8")
        await self.__rabbitmq_client.send_message(topic_name="Start", message_bytes=start_message_bytes)


async def start_platform_manager():
    """Starts the Simulation manager process."""
    platform_manager = PlatformManager()

    configuration_filename = cast(str, EnvironmentVariable("SIMULATION_CONFIGURATION_FILE", str).value)
    await platform_manager.start_simulation(configuration_filename)

    # await asyncio.sleep(TIMEOUT)
    await platform_manager.stop()
    # await asyncio.sleep(TIMEOUT)


if __name__ == "__main__":
    asyncio.run(start_platform_manager())
