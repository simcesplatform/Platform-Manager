#!/bin/bash
# Copyright 2021 Tampere University and VTT Technical Research Centre of Finland
# This software was developed as a part of the ProCemPlus project: https://www.senecc.fi/projects/procemplus
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Ville Heikkilä <ville.heikkila@tuni.fi>

# Fetches the Docker images and component manifest files for the domain component for the Simulation platform.
# Also makes the resource files available for the Simulation platform.

exists() {
    command -v "$1" >/dev/null 2>&1;
}

if exists "docker compose"
then
    compose_command="docker compose"
else
    compose_command="docker-compose"
fi

echo ""
echo "Fetching the domain Docker images from Docker registry"
source pull_docker_images.sh docker_images_domain.txt

echo ""
echo "Fetching the component manifests."
$compose_command --file fetch/docker-compose-fetch.yml up
$compose_command --file fetch/docker-compose-fetch.yml rm --force

echo ""
source copy_folder_to_volume.sh resources simces_simulation_resources /resources
