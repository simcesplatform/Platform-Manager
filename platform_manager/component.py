# -*- coding: utf-8 -*-

"""
This module contains data classes for storing information about the components that the Platform Manager supports.
"""

import dataclasses
from typing import Dict, Optional

CORE_COMPONENT_TYPE = "core"
DYNAMIC_COMPONENT_TYPE = "dynamic"
STATIC_COMPONENT_TYPE = "static"


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
    - component_type: the general type of the component, either "core", "dynamic" or "static"
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
    docker_image: Optional[str] = None
    attributes: Dict[str, ComponentAttribute] = dataclasses.field(default_factory=dict)
    include_rabbitmq_parameters: bool = True
    include_mongodb_parameters: bool = False
    include_general_parameters: bool = True
