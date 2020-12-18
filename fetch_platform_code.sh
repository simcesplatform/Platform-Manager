#!/bin/bash

current_folder=$(pwd)
read -p "Do you want clone the core component repositories to the folder $current_folder? [y/n] " answer
if [[ -z "$answer" ]] || [[ "$answer" != "y" ]]
then
    return 0 2> /dev/null || exit 0
fi

# Clones the core component repositories from the GitLab server
echo "Cloning the repositories"
git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/simulation-manager.git
git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/logwriter.git
git -c http.sslVerify=false clone https://git.ain.rd.tut.fi/procemplus/logreader.git
git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/platform-manager.git

# Simple checks to see if the repositories have been cloned properly
echo
if [ "$(ls -A simulation-manager/simulation-tools)" ]
then
    echo "OK: simulation-manager repository seems ok."
else
    echo "ERROR: Folder 'simulation-manager/simulation-tools' is empty!"
fi

if [ "$(ls -A logwriter/simulation-tools)" ]
then
    echo "OK: logwriter repository seems ok."
else
    echo "ERROR: Folder 'logwriter/simulation-tools' is empty!"
fi

if [ "$(ls -A logreader/LogReader)" ]
then
    echo "OK: logreader repository seems ok."
else
    echo "ERROR: Folder 'logreader/LogReader' is empty!"
fi

if [ "$(ls -A platform-manager/simulation-tools)" ]
then
    echo "OK: platform-manager repository seems ok."
else
    echo "ERROR: Folder 'platform-manager/simulation-tools' is empty!"
fi

# Set the certificate verification off for the cloned repositories
cd simulation-manager
git config http.sslVerify false --local
cd simulation-tools
git config http.sslVerify false --local
cd ../..

cd logwriter
git config http.sslVerify false --local
cd simulation-tools
git config http.sslVerify false --local
cd ../..

cd logreader
git config http.sslVerify false --local
cd ..

cd platform-manager
git config http.sslVerify false --local
cd simulation-tools
git config http.sslVerify false --local
cd ../..
