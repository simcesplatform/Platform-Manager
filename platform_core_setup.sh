#!/bin/bash

# Builds the core components and starts the background containers for the Simulation platform.

echo "Creating Docker volumes for the simulation platform."
docker volume create mongodb_data
docker volume create simulation_configuration
docker volume create simulation_resources
docker volume create simulation_logs

echo ""
echo "Creating Docker network for the simulation platform."
docker network create platform_network
docker network create mongodb_network
docker network create rabbitmq_network

echo ""
echo "Fetching the core Docker images from Docker registry"
source pull_docker_images.sh docker_images_core.txt

echo ""
echo "Starting the background Docker containers."
docker-compose -f background/docker-compose-background.yml up --detach

echo ""
echo "Fetching the component manifests."
docker-compose -f fetch/docker-compose-fetch.yml up
