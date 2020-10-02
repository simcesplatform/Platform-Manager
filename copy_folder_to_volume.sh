#!/bin/bash

folder=$1
volume_name=$2
volume_folder=$3

helper_container="file_copy_container"

echo "Copying the contents of '$folder' to Docker volume '$volume_name' to folder '$volume_folder'"
docker volume create $volume_name > /dev/null
docker run -d --name $helper_container --volume $volume_name:$volume_folder:rw ubuntu:18.04 sleep 10m > /dev/null

for filename in $(find $folder -type f | sed "s/$(echo "$folder/" | sed 's/\//\\\//g')//")
do
    echo "Copying file $folder/$filename"
    docker cp $folder/$filename $helper_container:$volume_folder/$filename > /dev/null
done

docker stop $helper_container > /dev/null
docker rm $helper_container > /dev/null
