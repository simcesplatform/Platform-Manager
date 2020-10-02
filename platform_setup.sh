#!/bin/bash

echo "Creating Docker volumes for the simulation platform."
docker volume create mongodb_data
docker volume create simulation_configuration
docker volume create simulation_resources
docker volume create simulation_logs

echo ""
echo "Creating Docker network for the simulation platform."
docker network create platform_network
docker network create mongodb_network

echo ""
echo "Building the required Docker images for the simulation platform."
docker-compose -f build/docker-compose-build-images.yml build

echo ""
source copy_folder_to_volume.sh resources simulation_resources /resources

echo ""
echo "Starting the background Docker containers."
docker-compose -f background/docker-compose-background.yml up --detach
