# -*- coding: utf-8 -*-

"""
This module contains data classes for storing the configuration for a single simulation run.
"""

import dataclasses
from typing import Any, Dict, Optional
import yaml

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
    """Data class for holding the general parameters, simulation name, epoch length, etc., for a simulation run."""
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
    """Data class for holding the parameters for one (either dynamic or static) component."""
    duplication_count: int = 1
    attributes: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SimulationComponentTypeConfiguration:
    """Data class for holding the names and parameters for one type of component."""
    components: Dict[str, SimulationComponentConfiguration] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SimulationConfiguration:
    """Data class for holding the configuration for a simulation run."""
    simulation: SimulationGeneralConfiguration
    components: Dict[str, SimulationComponentTypeConfiguration] = dataclasses.field(default_factory=dict)


def load_simulation_parameters_from_yaml(yaml_filename: str) -> SimulationConfiguration:
    """load_simulation_parameters_from_yaml"""
    with open(yaml_filename, mode="r", encoding="UTF-8") as yaml_file:
        yaml_configuration = yaml.safe_load(yaml_file)

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

    component_configurations = {
        component_type: SimulationComponentTypeConfiguration(
            components={
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
