#!/bin/bash

echo "Copying the simulation configuration file to the Platform Manager."
source copy_file_to_volume.sh simulation_configuration.yml simulation_configuration /configuration

echo "Starting the Platform Manager."
docker-compose --file docker-compose.yml up
