#!/bin/bash

# Fetches the Docker images and component manifest files for the domain component for the Simulation platform.
# Also makes the resource files available for the Simulation platform.

echo ""
echo "Fetching the domain Docker images from Docker registry"
source pull_docker_images.sh docker_images_domain.txt

echo ""
echo "Fetching the component manifests."
docker-compose -f fetch/docker-compose-fetch.yml up

echo ""
source copy_folder_to_volume.sh resources simulation_resources /resources
