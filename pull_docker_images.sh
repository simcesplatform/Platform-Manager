#!/bin/bash

# Pulls the given Docker images to the local machine.

if [ -z "$1" ]
then
    echo "Usage: source pull_docker_images.sh <file_with_docker_image_names>"
    return 0 2> /dev/null || exit 0
fi

input_file=$1
if ! test -f "$input_file"
then
    echo "Cannot find file '$input_file'"
    echo "Usage: source pull_docker_images.sh <file_with_docker_image_names>"
    return 0 2> /dev/null || exit 0
fi

echo "Reading '$input_file' for Docker image names"
while IFS= read -r docker_image || [ -n "$docker_image" ]
do
    first_character=${docker_image:0:1}
    # check that the current line is not a comment or empty line
    if [[ "$first_character" == "#" ]] || [[ "$docker_image" == "" ]]
    then
        continue
    fi

    docker pull $docker_image

done < "$input_file"
