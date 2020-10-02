#!/bin/bash

echo "Copying the simulation configuration file to the Platform Manager."
docker run -d --name configuration_access --volume simulation_configuration:/configuration ubuntu:18.04 sleep 10m > /dev/null
docker cp simulation_configuration.yml configuration_access:/configuration/simulation_configuration.yml > /dev/null
docker stop configuration_access > /dev/null
docker rm configuration_access > /dev/null

echo "Starting the Platform Manager."
docker-compose --file docker-compose.yml up --build
