#!/bin/bash

configuration_file=$1
platform_manager_env_file="common.env"

echo "Copying the simulation configuration file to the Platform Manager."
source copy_file_to_volume.sh $configuration_file simces_simulation_configuration /configuration

# Change the configuration file setting for Platform Manager.
sed -i "/SIMULATION_CONFIGURATION_FILE=/c\SIMULATION_CONFIGURATION_FILE=\/configuration\/${configuration_file}" ${platform_manager_env_file}

echo "Starting the Platform Manager."
docker-compose --file docker-compose.yml up
