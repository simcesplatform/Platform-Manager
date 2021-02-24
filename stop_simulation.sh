#!/bin/bash

# Script to stop a simulation run by stopping all the associated Docker containers.
# NOTE: this will not effect any external component participating in the simulation.
# NOTE: this will not remove the stopped containers

container_prefix="Sim${1}_"

for container in $(docker ps | awk '{print $NF}' | grep "${container_prefix}")
do
    docker stop ${container}
done
