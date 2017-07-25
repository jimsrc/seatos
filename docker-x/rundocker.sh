#!/bin/bash

# NOTE: this should be run from a host bash terminal.

me=`basename "$0"`

# repo path in the host && guest respectively
#REPO_HOST=${MEAN_PROFILES_ACE}
REPO_HOST=$ASO/icmes_richardson/data/mean_profiles/ace_docker
REPO_GUST=$HOME/seatos

HOME_GUST=/home/docker
XCONFIG_HOST=${REPO_HOST}/docker-x
XCONFIG_GUST=${HOME_GUST}/src
# name of out Docker image
DOCKER_IMAGE=jimsrc/conda:scipy


# define output-data paths for host && guest
DIRDATA_HOST=$1             # 1st argument
if [[ "${DIRDATA_HOST}" == "" ]]; then
    echo -e "\n [*] $me: data directory path not parsed from CLI. Generating default...\n"
    # default name for data directory
    DIRDATA_HOST=${XCONFIG_HOST}/data_`date +%d%b%Y_%H.%M.%S`   # host
fi
echo -e " [*] $me: creating output-data directory:\n     ${DIRDATA_HOST}\n"
mkdir -p ${DIRDATA_HOST}
DIRDATA_GUST=${HOME_GUST}/data      # guest


# let's hard-link data source to a local directory
# NOTE: give paths to files according to host space.
fnm_ACE=/work/data/ace.1998-2015.nc
fnm_MURDO=/work/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
fnm_AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
fnm_RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
fnm_HSTS=${AUGER_REPO}/build_temp.corr/final_histos.h5
fnm_SCLS=${AUGER_REPO}/scl.build_final/final_scalers.h5


# we'll only grab these data sets:
DataList=('ACE' 'MURDO' 'AVR' 'RICH_CSV' 'HSTS' 'SCLS')


# check that we got nothing in ${DIRDATA_HOST}
# NOTE: we should start with an empty data directory, because we
# are supposed to start fresh && clean.
nf=(`ls ${DIRDATA_HOST}`)
if [[ $nf -neq 0 ]]; then
    echo -e "\n [-] $me: Not empty data directory:\n     ${DIRDATA_HOST}"
    #_dirbckp=${DIRDATA_HOST}/../DataBckp_`date +%d%b%Y_%H.%M.%S`
    _dirbckp=${DIRDATA_HOST}_bckp_`date +%d%b%Y_%H.%M.%S`
    mkdir ${_dirbckp}
    echo -e " [*] $me: backing up to:\n     ${_dirbckp}\n"
    # back up && remove origin
    rsync -rvuthil --remove-source-files \
        --exclude=*.dat \
        --progress ${DIRDATA_HOST}/* ${_dirbckp}/.
    if [[ "$?" == "0" ]]; then
        echo -e "\n [+] $me: back up finished OK!\n"
    else
        echo -e "\n [-] ERROR (@ $me): rsync exited with status:$?\n"
        exit 1
    fi
    # remove remaining files
    rm -rf ${DIRDATA_HOST}/*
elif [[ -d ${DIRDATA_HOST} ]]; then
    echo -e "\n [+] $me: OK: data directory is empty!\n"
else
    echo -e "\n [-] $me: data directory doesn't exist:\n ${DIRDATA_HOST}\n"
    exit 1
fi



# docker-run arguments to pass Environment variables to pass
# the paths (in guest space) to data files
ArgsEnv=""

# we'll hard-link each data source into ${DIRDATA_HOST}
nData=${#DataList[@]}
for id in $(seq 0 1 $(($nData-1))); do
    dnm=${DataList[$id]}            # data name
    vfnm=fnm_"$dnm"                 # variable name for filename
    fnm_src=${!vfnm}                # filename of data
    echo -e " > $dnm:\n ${fnm_src}"
    # hard-link using the realpath of the source filename
    ln -f "$(realpath ${fnm_src})" ${DIRDATA_HOST}/$dnm.dat
    if [[ $? -eq 0 ]]; then
        echo -e " [+] hard-link ok!\n"
    else
        echo -e " [-] ERROR with hard-link! (status:$?)\n" && exit 1
    fi
    ArgsEnv+="--env $dnm=${DIRDATA_GUST}/$dnm.dat "
done

echo -e "\n [+] $me: Environment variables we'll parse to Docker:\n $ArgsEnv\n"


# script to run inside Docker
SCRIPT=${REPO_GUST}/docker-x/docker_test.sh

# run Docker image in a container
docker run --rm -t \
    --name ubuntuX2 \
    --user=$UID:$GID \
    --volume=${XCONFIG_HOST}:${XCONFIG_GUST}    --env XCONFIG=${XCONFIG_GUST} \
    --volume=${REPO_HOST}:${REPO_GUST}          --env MEAN_PROFILES_ACE=${REPO_GUST} \
    --volume=${DIRDATA_HOST}:${DIRDATA_GUST}    --env DIRDATA=${DIRDATA_GUST} \
    $ArgsEnv \
    -w ${HOME_GUST} \
    ${DOCKER_IMAGE} \
    ${SCRIPT}

echo -e " [+] $me: All generated data is in:\n ${DIRDATA_HOST}"

#--- delete hard-links
#rm ${DIRDATA_HOST}/*


#EOF
