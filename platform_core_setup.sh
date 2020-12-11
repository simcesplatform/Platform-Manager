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
echo "Building the core Docker images for the simulation platform."
docker-compose -f build/core/docker-compose-build-core.yml build

echo ""
echo "Starting the background Docker containers."
docker-compose -f background/docker-compose-background.yml up --detach
