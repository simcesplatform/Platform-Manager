#!/bin/bash

filename=$1
volume_name=$2
volume_folder=$3

helper_container="file_copy_container"

echo "Copying '$filename' to Docker volume '$volume_name' to folder '$volume_folder'"
docker volume create $volume_name > /dev/null
docker run -d --name $helper_container --volume $volume_name:$volume_folder:rw ubuntu:18.04 sleep 10m > /dev/null

docker cp $filename $helper_container:$volume_folder/$filename > /dev/null

docker stop $helper_container > /dev/null
docker rm $helper_container > /dev/null
