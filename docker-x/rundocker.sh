#!/bin/bash

# NOTE: this should be run from a host bash terminal.

# repo path in the host && guest respectively
#REPO_HOST=${MEAN_PROFILES_ACE}
REPO_HOST=$ASO/icmes_richardson/data/mean_profiles/ace_docker
REPO_GUST=$HOME/seatos

HOME_GUST=/home/docker
XCONFIG_HOST=${REPO_HOST}/docker-x
XCONFIG_GUST=${HOME_GUST}/src
# name of out Docker image
DOCKER_IMAGE=jimsrc/conda:scipy
# script to run inside Docker
SCRIPT=${REPO_GUST}/docker-x/docker_test.sh

# run Docker image in a container
docker run --rm -t \
    --name ubuntuX2 \
    --user=$UID:$GID \
    --volume=${XCONFIG_HOST}:${XCONFIG_GUST} \
    --env XCONFIG=${XCONFIG_GUST} \
    --volume=${REPO_HOST}:${REPO_GUST} \
    --env MEAN_PROFILES_ACE=${REPO_GUST} \
    -w ${HOME_GUST} \
    ${DOCKER_IMAGE} \
    ${SCRIPT}

#docker run -it \
#    --name ubuntuX2 \
#    --user=$UID:$GID \
#    --volume=${XCONFIG_HOST}:${XCONFIG_GUST} \
#    --env XCONFIG=${XCONFIG_GUST} \
#    --volume=${REPO_HOST}:${REPO_GUST} \
#    --env MEAN_PROFILES_ACE=${REPO_GUST} \
#    -w ${HOME_GUST} \
#    ${DOCKER_IMAGE} \
#    ${SCRIPT}


#EOF
