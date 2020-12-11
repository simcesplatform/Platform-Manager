#!/bin/bash

# Builds the domain components and makes the resource files available for the Simulation platform.

echo "Building the domain Docker images for the simulation platform."
docker-compose -f build/domain/docker-compose-build-domain.yml build

echo ""
source copy_folder_to_volume.sh resources simulation_resources /resources

echo ""
echo "Starting the background Docker containers."
docker-compose -f background/docker-compose-background.yml up --detach
