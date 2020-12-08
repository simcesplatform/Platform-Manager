# -*- coding: utf-8 -*-

"""
This module contains data classes for storing information about the components that the Platform Manager supports.
"""

import dataclasses
import json
from typing import Dict, Optional

from tools.tools import FullLogger

LOGGER = FullLogger(__name__)

CORE_COMPONENT_TYPE = "core"        # there can be only one component of each "core" type within one simulation run
DYNAMIC_COMPONENT_TYPE = "dynamic"  # a component deployed using Docker, multiple instances of each type allowed
STATIC_COMPONENT_TYPE = "static"    # a statically deployed component, multiple instances of each type allowed
ALLOWED_COMPONENT_TYPES = [CORE_COMPONENT_TYPE, DYNAMIC_COMPONENT_TYPE, STATIC_COMPONENT_TYPE]

COMPONENT_TYPE_SIMULATION_MANAGER = "SimulationManager"
COMPONENT_TYPE_LOG_WRITER = "LogWriter"

PARAMETER_COMPONENT_TYPE = "Type"
PARAMETER_DESCRIPTION = "Description"
PARAMETER_DOCKER_IMAGE = "DockerImage"
PARAMETER_ATTRIBUTES = "Attributes"

ATTRIBUTE_ENVIRONMENT = "Environment"
ATTRIBUTE_OPTIONAL = "Optional"
ATTRIBUTE_DEFAULT = "Default"


@dataclasses.dataclass
class ImageName:
    """Dataclass for holding Docker image name including the tag part."""
    image_name: str
    image_tag: str = "latest"

    @property
    def full_name(self) -> str:
        """The full Docker image name including the tag."""
        return ":".join([self.image_name, self.image_tag])


@dataclasses.dataclass
class ComponentAttribute:
    """
    Data class for holding information about an attribute for a component type.
    - environment: a string corresponding to the environmental variable name for the attribute,
                   should be None for an attribute for a static component
    - optional: a boolean value telling whether the attribute is optional or not
    - default: a string representing the default value for the attribute,
               all optional attributes should have a default value
    """
    environment: Optional[str] = None
    optional: bool = False
    default: Optional[str] = None


@dataclasses.dataclass
class ComponentParameters:
    """
    Data class for holding information about the parameters for a simulation component.
    - component_type: the general deployment type of the component, either "core", "dynamic" or "static"
    - description: a description for the component type
    - docker_image: a string representing the Docker image to be used with the component type,
                    should be None for a static component type
    - attributes: a dictionary containing the information about the input parameters for the component type,
                  any attribute not listed here is assumed to be optional and the corresponding environmental
                  variable name for an omitted attribute is assumed to be the same as the attribute name given
                  in the simulation configuration
    - include_rabbitmq_parameters: whether to pass the RabbitMQ connection parameters for a dynamic component
    - include_mongodb_parameters: whether to pass the MongoDB connection parameters for a dynamic component
    - include_general_parameters: whether to pass the general environmental variables for a dynamic component,
                                  this should be True for any component inherited from AbstractSimulationComponent,
                                  these include simulation id, component name and the logging level
    """
    component_type: str
    description: str = ""
    docker_image: Optional[ImageName] = None
    attributes: Dict[str, ComponentAttribute] = dataclasses.field(default_factory=dict)
    include_rabbitmq_parameters: bool = True
    include_mongodb_parameters: bool = False
    include_general_parameters: bool = True


@dataclasses.dataclass
class ComponentCollectionParameters:
    """
    Data class for holding information about the supported component types and their parameters.
    - component_types: a dictionary containing information about each of the supported component types
    """
    component_types: Dict[str, ComponentParameters] = dataclasses.field(default_factory=dict)


def load_component_parameters_from_json(json_filename: str) -> ComponentCollectionParameters:
    """Loads and returns the component type specification from a JSON file."""
    component_types = {}
    try:
        with open(json_filename, mode="r", encoding="UTF-8") as component_file:
            component_type_definitions = json.load(component_file)
            for component_type, component_type_definition in component_type_definitions.items():
                deployment_type = component_type_definition.get(PARAMETER_COMPONENT_TYPE, None)
                if deployment_type not in ALLOWED_COMPONENT_TYPES:
                    LOGGER.warning("Component type '{}' has an unsupported deployment type: {}".format(
                        component_type, deployment_type
                    ))
                    continue

                # TODO: add some validation checks for the other parameters in the JSON file

                docker_image = component_type_definition.get(PARAMETER_DOCKER_IMAGE, None)
                if docker_image is not None:
                    docker_image = ImageName(*docker_image.split(":"))
                component_types[component_type] = ComponentParameters(
                    component_type=deployment_type,
                    description=component_type_definition.get(PARAMETER_DESCRIPTION, ""),
                    docker_image=docker_image,
                    attributes={
                        attribute_name: ComponentAttribute(
                            environment=attribute_definition.get(ATTRIBUTE_ENVIRONMENT, None),
                            optional=attribute_definition.get(ATTRIBUTE_DEFAULT, False),
                            default=attribute_definition.get(ATTRIBUTE_DEFAULT, None)
                        )
                        for attribute_name, attribute_definition in component_type_definition.get(
                            PARAMETER_ATTRIBUTES, {}).items()
                    },
                    include_rabbitmq_parameters=deployment_type != STATIC_COMPONENT_TYPE,
                    include_mongodb_parameters=component_type == COMPONENT_TYPE_LOG_WRITER,
                    include_general_parameters=deployment_type != STATIC_COMPONENT_TYPE
                )

        LOGGER.debug("Loaded definitions for {} component types from {}".format(len(component_types), json_filename))

    except (OSError, json.decoder.JSONDecodeError) as json_error:
        LOGGER.error("Encountered '{}' exception when loading component type definitions from '{}': {}".format(
            str(type(json_error)), json_filename, json_error
        ))

    return ComponentCollectionParameters(component_types)
