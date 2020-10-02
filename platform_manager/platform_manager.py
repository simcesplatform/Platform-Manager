# -*- coding: utf-8 -*-

"""This module contains the Platform Manager code that handles the starting of the simulation components for
   a simulation using the simulation platform.
"""

import asyncio
import logging
from typing import cast, Any, Dict, List

import yaml

from platform_manager.docker_runner import ContainerConfiguration, ContainerStarter
from tools.clients import default_env_variable_definitions as default_rabbitmq_definitions
from tools.datetime_tools import get_utcnow_in_milliseconds, to_iso_format_datetime_string
from tools.db_clients import default_env_variable_definitions as default_mongodb_definitions
from tools.tools import FullLogger, load_environmental_variables, EnvironmentVariable

LOGGER = FullLogger(__name__)

EXCHANGE_PREFIX = cast(str, EnvironmentVariable("RABBITMQ_EXCHANGE_PREFIX", str, "procem.").value)


def get_simulation_exchange_name(simulation_id: str) -> str:
    """Returns the name for the simulation specific exchange."""
    return (
        EXCHANGE_PREFIX +
        simulation_id.replace("-", "").replace(":", "").replace("Z", "").replace("T", "-").replace(".", "-")
    )


def get_component_log_filename(main_log_filename: str, component_name: str) -> str:
    """Returns the log filename for the given component."""
    filename_addition = "_" + component_name
    identifier_start = main_log_filename.rfind(".")
    if identifier_start == -1:
        return main_log_filename + filename_addition
    return main_log_filename[:identifier_start] + filename_addition + main_log_filename[identifier_start:]


def create_container_configuration(component_name: str, component_image: str,
                                   component_environment: Dict[str, Any],
                                   docker_networks: List[str],
                                   docker_volumes: Dict[str, str]) -> ContainerConfiguration:
    """Creates a configuration object for a new Docker container."""
    configuration = ContainerConfiguration(
        component_name, component_image, component_environment, docker_networks, docker_volumes)
    return configuration


async def start_platform_manager():
    """Starts the Simulation manager process."""
    configuration_file_name = cast(str, EnvironmentVariable("SIMULATION_CONFIGURATION_FILE", str).value)
    with open(configuration_file_name, mode="r", encoding="utf-8") as configuration_yaml_file:
        simulation_configuration = yaml.safe_load(configuration_yaml_file)

    simulation_id = get_utcnow_in_milliseconds()
    main_log_filename = cast(str, EnvironmentVariable("SIMULATION_LOG_FILE", str, "logfile.log").value)
    simulation_start_time = to_iso_format_datetime_string(simulation_configuration["simulation"]["start_time"])
    if simulation_start_time is None:
        LOGGER.error("Invalid simulation start time: {:s}".format(simulation_start_time))
        return

    # setup the RabbitMQ parameters for the simulation specific exchange
    rabbitmq_env_variables = load_environmental_variables(*default_rabbitmq_definitions())
    rabbitmq_component_environment = {
        **rabbitmq_env_variables,
        "RABBITMQ_EXCHANGE": get_simulation_exchange_name(simulation_id),
        "RABBITMQ_EXCHANGE_AUTODELETE": "true",
        "RABBITMQ_EXCHANGE_DURABLE": "false"
    }

    mongodb_environment = load_environmental_variables(*default_mongodb_definitions())

    common_env_variables = load_environmental_variables(
        ("SIMULATION_LOG_LEVEL", str, logging.INFO),
        ("SIMULATION_EPOCH_MESSAGE_TOPIC", str, "Epoch"),
        ("SIMULATION_STATUS_MESSAGE_TOPIC", str, "Status"),
        ("SIMULATION_STATE_MESSAGE_TOPIC", str, "SimState"),
        ("SIMULATION_ERROR_MESSAGE_TOPIC", str, "Error")
    )
    common_component_environment = {
        **rabbitmq_component_environment,
        **common_env_variables,
        "SIMULATION_ID": simulation_id
    }

    simulation_component_names = []
    simulation_component_settings = []
    for component_name, component_parameters in simulation_configuration["processes"].items():
        component_image = str(component_parameters["image"])
        component_count = int(component_parameters.get("count", 1))
        component_specific_env_variables = component_parameters.get("environment", {})

        for index in range(1, component_count + 1):
            if component_count == 1:
                full_component_name = component_name
            else:
                full_component_name = "_".join([component_name, str(index)])

            component_specific_environment = {
                **common_component_environment,
                "SIMULATION_LOG_FILE": get_component_log_filename(
                    main_log_filename, full_component_name),
                **component_specific_env_variables,
                "SIMULATION_COMPONENT_NAME": full_component_name
            }
            simulation_component_names.append(full_component_name)
            simulation_component_settings.append((
                full_component_name,
                component_image,
                component_specific_environment
            ))

    manager_env_variables = load_environmental_variables(
        ("SIMULATION_MANAGER_NAME", str),
        ("SIMULATION_EPOCH_TIMER_INTERVAL", float, 30.0),
        ("SIMULATION_MAX_EPOCH_RESENDS", int, 5),
    )
    simulation_manager_name = cast(str, manager_env_variables["SIMULATION_MANAGER_NAME"])
    manager_environment = {
        **common_component_environment,
        **manager_env_variables,
        "SIMULATION_NAME": simulation_configuration["simulation"]["name"],
        "SIMULATION_DESCRIPTION": simulation_configuration["simulation"]["description"],
        "SIMULATION_COMPONENTS": ",".join(simulation_component_names),
        "SIMULATION_INITIAL_START_TIME": simulation_start_time,
        "SIMULATION_EPOCH_LENGTH": simulation_configuration["simulation"]["epoch_length"],
        "SIMULATION_MAX_EPOCHS": simulation_configuration["simulation"]["max_epochs"],
        "SIMULATION_LOG_FILE": get_component_log_filename(main_log_filename, simulation_manager_name)
    }
    manager_settings = (
        simulation_manager_name,
        str(simulation_configuration["simulation"]["manager_image"]),
        manager_environment
    )

    logwriter_env_variables = load_environmental_variables(
        ("MESSAGE_BUFFER_MAX_DOCUMENTS", int, 10),
        ("MESSAGE_BUFFER_MAX_INTERVAL", float, 5.0)
    )
    logwriter_name = cast(str, mongodb_environment["MONGODB_APPNAME"])
    logwriter_environment = {
        **common_component_environment,
        **mongodb_environment,
        **logwriter_env_variables,
        "SIMULATION_LOG_FILE": get_component_log_filename(main_log_filename, logwriter_name)
    }
    logwriter_settings = (
        logwriter_name,
        str(simulation_configuration["simulation"]["logwriter_image"]),
        logwriter_environment
    )

    all_component_settings = [logwriter_settings] + simulation_component_settings + [manager_settings]

    docker_env_variables = load_environmental_variables(
        ("DOCKER_NETWORK_MONGODB", str),
        ("DOCKER_NETWORK_RABBITMQ", str),
        ("DOCKER_VOLUME_NAME_RESOURCES", str),
        ("DOCKER_VOLUME_NAME_LOGS", str),
        ("DOCKER_VOLUME_TARGET_RESOURCES", str),
        ("DOCKET_VOLUME_TARGET_LOGS", str)
    )
    docker_networks = {
        "mongodb": docker_env_variables["DOCKER_NETWORK_MONGODB"],
        "rabbitmq": docker_env_variables["DOCKER_NETWORK_RABBITMQ"]
    }
    resource_volume = {
        cast(str, docker_env_variables["DOCKER_VOLUME_NAME_RESOURCES"]):
            cast(str, docker_env_variables["DOCKER_VOLUME_TARGET_RESOURCES"])
    }
    logs_volume = {
        cast(str, docker_env_variables["DOCKER_VOLUME_NAME_LOGS"]):
            cast(str, docker_env_variables["DOCKET_VOLUME_TARGET_LOGS"])
    }

    container_configuration_list = []
    for component_name, component_image, component_environment in all_component_settings:
        component_networks = []
        if docker_networks["rabbitmq"]:
            component_networks.append(docker_networks["rabbitmq"])
        if component_name == logwriter_name:
            component_networks.append(docker_networks["mongodb"])

        component_volumes = logs_volume
        if component_name != simulation_manager_name and component_name != logwriter_name:
            component_volumes = {**component_volumes, **resource_volume}

        container_configuration = create_container_configuration(
            component_name, component_image, component_environment, component_networks, component_volumes)
        container_configuration_list.append(container_configuration)

    LOGGER.info("Starting the containers")
    container_starter = ContainerStarter()
    container_names = await container_starter.start_simulation(container_configuration_list)

    if container_names is None:
        LOGGER.error("A problem starting the simulation.")
        return

    manager_container_name = container_names[-1]
    LOGGER.info("Simulation started successfully.")
    LOGGER.info("Follow the simulation through the simulation manager by using the command:\n" +
                "docker attach {:s}".format(manager_container_name))

    await asyncio.sleep(5.0)
    await container_starter.close()
    await asyncio.sleep(5.0)


if __name__ == "__main__":
    asyncio.run(start_platform_manager())
