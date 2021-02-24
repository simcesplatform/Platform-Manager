#!/bin/bash

# Fetches the given local component manifest files and copies them to the manifests folder.

if [ -z "$1" ]
then
    echo "Usage: source fetch_local_manifests.sh <file_with_manifest_file_list>"
    return 0 2> /dev/null || exit 0
fi

input_file=$1
if ! test -f "$input_file"
then
    echo "Cannot find file '$input_file'"
    echo "Usage: source fetch_local_manifests.sh <file_with_manifest_file_list>"
    return 0 2> /dev/null || exit 0
fi

manifest_folder="manifests/local"

echo "Reading '$input_file' for local component manifest files"
while read -r manifest_file
do
    first_character=${manifest_file:0:1}
    # check that the current line is not a comment or empty line
    if [[ "$first_character" == "#" ]] || [[ "$manifest_file" == "" ]]
    then
        continue
    fi

    if test -f "$manifest_file"
    then
        file_suffix=$(echo "$manifest_file" | rev | cut --delimiter="." --fields=1 | rev)

        # check that the manifest filename contains a suffix
        if [[ "$file_suffix" != "$manifest_file" ]]
        then
            # check that the manifest filename suffix corresponds to a YAML file
            if [[ "$file_suffix" == "yml" ]] || [[ "$file_suffix" == "yaml" ]]
            then
                filename=$(echo "$manifest_file" | rev | cut --delimiter="/" --fields=1 | rev)
                component_folder=$(echo "$manifest_file" | rev | cut --delimiter="/" --fields=2 | rev)

                # use the second to last part of the manifest file path as the component name for the target folder
                if [[ $component_folder != *"."* ]]
                then
                    target_folder="$manifest_folder/$component_folder"
                else
                    target_folder="$manifest_folder"
                fi
                target_file=$target_folder/$filename

                echo "Copying '$manifest_file' to '$target_file'"
                mkdir -p $target_folder
                cp $manifest_file $target_file

            else
                echo "File '$manifest_file' does not have the suffix '.yml' or '.yaml'"
            fi

        else
            echo "File '$manifest_file' does contain a suffix"
        fi

    else
        echo "Cannot find file '$manifest_file'"
    fi

done < "$input_file"
