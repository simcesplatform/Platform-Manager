# -*- coding: utf-8 -*-

"""
This module contains data classes for storing the configuration for a single simulation run.
"""

import dataclasses
from typing import Any, Dict, Optional
import yaml
import yaml.parser

from tools.datetime_tools import get_utcnow_in_milliseconds
from tools.tools import FullLogger

LOGGER = FullLogger(__name__)

# The main attributes in simulation configuration file
SIMULATION = "Simulation"
COMPONENTS = "Components"

# The overall simulation attributes in the simulation configuration file
SIMULATION_NAME = "Name"
SIMULATION_DESCRIPTION = "Description"
SIMULATION_START_TIME = "InitialStartTime"
SIMULATION_EPOCH_LENGTH = "EpochLength"
SIMULATION_MAX_EPOCH_COUNT = "MaxEpochCount"

# The optional parameters for the simulation manager in the simulation configuration file
SIMULATION_MANAGER_NAME = "ManagerName"
SIMULATION_EPOCH_TIMER_INTERVAL = "EpochTimerInterval"
SIMULATION_MAX_EPOCH_RESEND_COUNT = "MaxEpochResendCount"

# The optional parameters for the log writer in the simulation configuration file
MESSAGE_BUFFER_MAX_DOCUMENTS = "MessageBufferMaxDocumentCount"
MESSAGE_BUFFER_MAX_INTERVAL = "MessageBufferMaxInterval"

# The special attribute that can be used to create multiple identical components for the simulation
DUPLICATION_COUNT = "duplication_count"


@dataclasses.dataclass
class SimulationGeneralConfiguration:
    """
    Data class for holding the general parameters, simulation name, epoch length, etc., for a simulation run.
    - simulation_id: the id for the simulation run
    - initial_start_time: the start time for the first epoch in ISO 8601 format
    - epoch_length: the length of each epoch in seconds
    - max_epoch_count: the maximum number of epochs within the simulation run
    - simulation_name: the name of the simulation
    - description: a descripton for the simulation
    - manager_name: the name of the simulation manager within the simulation run
    - epoch_timer_interval: the time interval in seconds until simulation manager resends an Epoch message
                            if some component has not responded with a Status message
    - max_epoch_resend_count: the maximum number of Epoch message resends simulation manager can try before giving up
    - message_bugger_max_document_count: maximum number of messages kept in a buffer in the log writer
    - message_buffer_max_interval: maximum number of seconds until message buffer is cleared in the log writer
    """
    simulation_id: str
    initial_start_time: str
    epoch_length: int
    max_epoch_count: int

    simulation_name: str = "simulation"
    description: str = ""

    manager_name: Optional[str] = None
    epoch_timer_interval: Optional[float] = None
    max_epoch_resend_count: Optional[int] = None

    message_bugger_max_document_count: Optional[int] = None
    message_buffer_max_interval: Optional[float] = None


@dataclasses.dataclass
class SimulationComponentConfiguration:
    """
    Data class for holding the parameters for one (either dynamic or static) component.
    - duplication_count: how many identical duplicates will be participating in the simulation run, default is 1
    - attributes: a dictionary containing the attribute names and values for the component
    """
    duplication_count: int = 1
    attributes: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SimulationComponentTypeConfiguration:
    """
    Data class for holding the names and parameters for the processes of one type of component
    participating in the simulation run.
    - processes: a dictionary containing the parameters for the participating processes
    """
    processes: Dict[str, SimulationComponentConfiguration] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SimulationConfiguration:
    """
    Data class for holding the configuration for a single simulation run.
    - simulation: the general specification parameters for the simulation run
    - components: a dictionary containing the parameters for all the participating components
    """
    simulation: SimulationGeneralConfiguration
    components: Dict[str, SimulationComponentTypeConfiguration] = dataclasses.field(default_factory=dict)


def load_simulation_parameters_from_yaml(yaml_filename: str) -> Optional[SimulationConfiguration]:
    """
    Loads and returns the simulation run specification from a YAML file.
    Returns None, if there is a problem loading the simulation parameters.
    """
    try:
        with open(yaml_filename, mode="r", encoding="UTF-8") as yaml_file:
            yaml_configuration = yaml.safe_load(yaml_file)

        # load the general configuration parameters for the simulation run
        simulation_general_configuration = yaml_configuration.get(SIMULATION, {})
        general_configuration = SimulationGeneralConfiguration(
            simulation_id=get_utcnow_in_milliseconds(),
            initial_start_time=simulation_general_configuration[SIMULATION_START_TIME],
            epoch_length=simulation_general_configuration[SIMULATION_EPOCH_LENGTH],
            max_epoch_count=simulation_general_configuration[SIMULATION_MAX_EPOCH_COUNT],
            simulation_name=simulation_general_configuration.get(SIMULATION_NAME, "simulation"),
            description=simulation_general_configuration.get(SIMULATION_DESCRIPTION, ""),
            manager_name=simulation_general_configuration.get(SIMULATION_MANAGER_NAME, None),
            epoch_timer_interval=simulation_general_configuration.get(SIMULATION_EPOCH_TIMER_INTERVAL, None),
            max_epoch_resend_count=simulation_general_configuration.get(SIMULATION_MAX_EPOCH_RESEND_COUNT, None),
            message_bugger_max_document_count=simulation_general_configuration.get(MESSAGE_BUFFER_MAX_DOCUMENTS, None),
            message_buffer_max_interval=simulation_general_configuration.get(MESSAGE_BUFFER_MAX_INTERVAL, None)
        )

        # load the component specific parameters for the simulation run
        component_configurations = {
            component_type: SimulationComponentTypeConfiguration(
                processes={
                    component_name: SimulationComponentConfiguration(
                        duplication_count=component_attributes.get(DUPLICATION_COUNT, 1),
                        attributes={
                            attribute_name: attribute_value
                            for attribute_name, attribute_value in component_attributes.items()
                            if attribute_name != DUPLICATION_COUNT
                        }
                    )
                    for component_name, component_attributes in component_type_processes.items()
                }
            )
            for component_type, component_type_processes in yaml_configuration.get(COMPONENTS, {}).items()
        }

        return SimulationConfiguration(
            simulation=general_configuration,
            components=component_configurations
        )

    except (OSError, KeyError, yaml.parser.ParserError) as yaml_error:
        LOGGER.error("Encountered '{}' exception when loading simulation run specification from '{}': {}".format(
            str(type(yaml_error)), yaml_filename, yaml_error
        ))
        return None
