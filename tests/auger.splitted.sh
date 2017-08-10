#!/bin/bash
#++++++++++++++++++++++++++++++++++++++++++++
#
# This script extracts data for ICME passages, from
# original ACE datasets. Also creates auxiliary
# histograms and average values appended in the 
# output files.
#
#++++++++++++++++++++++++++++++++++++++++++++

me=`basename "$0"` # name of this script


# output diretory
OUTDIR=$1      # 1st argument


if [[ -d "$OUTDIR" ]]; then
    echo -e "\n [+] $me: output directory ok:\n $OUTDIR\n"
else
    echo -e "\n [-] $me: output directory doesn't exist:\n $OUTDIR\n"
    exit 1
fi

#--- check that all data paths are set:
[[ -v ACE && -v MURDO && -v AVR && -v RICH_CSV && -v AUGER_REPO && -v HSTS && -v SCLS ]] \
    && ok=true \
    || ok=false
if [[ ! $ok ]]; then
    # if any of them is not set, set them all
    # NOTE: this is in *case* we are running on host (real) machine
    echo -e "\n [-] $me: At least one env variable is not present, so"
    echo -e "     we'll set them...\n"
    export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
    export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
    export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
    export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
    export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
    export SCLS=$AUGER_REPO/scl.build_final/test_iv.h5 # newest version
else
    echo -e "\n [+] $me: all needed env variables were parsed to this script!\n"
fi


# NOTE: arguments for --Vsplit are 'VarName ThresLower ThresUpper':
vsplit='mc_V 450. 550.' # these 2 limits define the partition into 3 groups
dir_out=$OUTDIR # output directory

EXE=${MEAN_PROFILES_ACE}/one.structure/src/sea_splitted.py
for struct in sh.mc mc; do
    echo -e "\n [*] $me: running for structure: ($struct) ...\n"
    #--- run for the 3 subgroups && the global one
    $EXE --pdb -- \
        -ace $ACE -ace1sec 0 -murdo $MURDO  -avr $AVR  --rich_csv $RICH_CSV \
        -ahs 0  -ahm 0 -as 0 \
        --dir_plot ${dir_out}  \
        --dir_data ${dir_out}  \
        --suffix _${struct}_  \
        --icme_flag 2  \
        --struct $struct  \
        --wang 1 90.  \
        --Vsplit $vsplit  \
        --tshift \
        --fgap 0.2

    echo -e "\n [*] $me: exit status: ($?)\n"
    # interrupt if something went work!
    [[ $? -ne 0 ]] && exit 1
done

#EOF
