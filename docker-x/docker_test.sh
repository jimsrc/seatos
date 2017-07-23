#!/bin/bash
#++++++++++++++++++++++++++++++++++++++++++++
#
# This script is for running inside a Docker container.
#
#++++++++++++++++++++++++++++++++++++++++++++

#--
echo -e "\n [+] we are IN!\n"

# start the DISPLAY:
DISP=10
$XCONFIG/config/docker-desktop -s 800x600 -d $DISP

# since `source ~/.bashrc` doesn't work, we append to PATH manually:
export PATH="$HOME/miniconda2/bin:$PATH"

# switch to our Conda environment for work
echo -e "\n [*] switching to our conda env...\n"
source activate work 
if [[ "$?" == "0" ]]; then
    echo -e "\n [+] OK!, we'll use:\n $(which ipython)\n"
else
    echo -e "\n [-] we couldn't load the conda env!\n"
    return 1
fi

#-- set data paths:
if [[ ! -v DATADIR ]]; then
    echo -e "\n [-] ERROR: we need DATASET env variable!\n"
    exit 1
fi
export ACE=$DATADIR/ACE/ace.1998-2015.nc
export MURDO=$DATADIR/MURDO/mcmurdo_utc_correg.dat
export AVR=$DATADIR/AVR/rich_events2_ace.nc
export RICH_CSV=$DATADIR/RICH_CSV/RichardsonList_until.2016.csv
export HSTS=$DATADIR/HSTS/final_histos.h5
export SCLS=$DATADIR/SCLS/final_scalers.h5


#--- script that extracts data from ICMEs/MCs/sheaths passages
echo -e "\n [*] starting script for event data extraction...\n"
DISPLAY=:$DISP ${MEAN_PROFILES_ACE}/tests/auger.splitted.sh


#--- script that builds mixed profiles
# export LEFT, RIGHT, OUTDIR, etc...
echo -e "\n [*] starting script to build mixed profiles...\n"
#DISPLAY=:$DISP ${MEAN_PROFILES_ACE}/tests/auger.solphys.sh

#EOF
