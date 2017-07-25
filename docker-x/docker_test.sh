#!/bin/bash
#++++++++++++++++++++++++++++++++++++++++++++
#
# This script is for running inside a Docker container.
#
#++++++++++++++++++++++++++++++++++++++++++++

#--
me=`basename "$0"`
echo -e "\n [+] $me: we are inside Docker!\n"

# start the DISPLAY:
DISP=10
$XCONFIG/config/docker-desktop -s 800x600 -d $DISP


# since `source ~/.bashrc` doesn't work, we append to PATH manually:
export PATH="$HOME/miniconda2/bin:$PATH"


# switch to our Conda environment for work
echo -e "\n [*] $me: switching to our conda env...\n"
source activate work 
if [[ "$?" == "0" ]]; then
    echo -e "\n [+] $me: OK!, we'll use:\n $(which ipython)\n"
else
    echo -e "\n [-] $me: we couldn't load the conda env!\n"
    return 1
fi


#-- set data paths:
if [[ ! -v DIRDATA && -v MEAN_PROFILES_ACE ]]; then
    echo -e "\n [-] $me: ERROR: we need DIRDATA && MEAN_PROFILES_ACE env variables!\n"
    exit 1
fi


#--- extracts data from ICMEs/MCs/sheaths passages
OUT_EventsData=$DIRDATA/EventsData && mkdir ${OUT_EventsData}
echo -e "\n [*] $me: starting script for event data extraction...\n"
DISPLAY=:$DISP ${MEAN_PROFILES_ACE}/tests/auger.splitted.sh ${OUT_EventsData}


#--- builds the mixed profiles
export LEFT=${OUT_EventsData}/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=${OUT_EventsData}/MCflag0.1.2.2H/woShiftCorr/_i_
OUT_MixProfs=$DIRDATA/MixProfs && mkdir ${OUT_MixProfs}
echo -e "\n [*] $me: starting script to build mixed profiles...\n"
DISPLAY=:$DISP ${MEAN_PROFILES_ACE}/tests/auger.solphys.sh ${OUT_MixProfs}

#EOF
