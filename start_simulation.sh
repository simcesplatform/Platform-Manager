#!/bin/bash

configuration_file=$1

echo "Copying the simulation configuration file to the Platform Manager."
source copy_file_to_volume.sh $configuration_file simulation_configuration /configuration

echo "Starting the Platform Manager."
docker-compose --file docker-compose.yml up
