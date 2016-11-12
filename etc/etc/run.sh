#!/bin/bash
export AVR=./data/rich_events2_ace.nc
export RICH_CSV=./data/RichardsonList_until.2016.csv
export ACE1sec=$HOME/data_ace/mag_data_1sec
export ACE=$HOME/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export ASO=none
export PAO=none

lims=('100. 450.' '450. 550.' '550. 3000.' '100. 3000.')
prex=(lo mid hi all) # prefix

#--- beta
for struct in sh.mc mc; do
    for il in $(seq 0 1 3); do
        #echo _pascal_mid/${struct}_${prex[$il]}
        #--- ACE
        ./extract_struct.py -- -avr $AVR -rich $RICH_CSV --inp_name ACE --input $ACE --icme_flag 2  --struct $struct  -ba 2 4  --obs beta  --tshift  -lim ${lims[$il]}  --dir_data _pascal_/${struct}_${prex[$il]}  --wang 90.
        #--- ACE1sec
        ./extract_struct.py -- -avr $AVR -rich $RICH_CSV --inp_name ACE1sec --input $ACE1sec --icme_flag 2  --struct $struct  -ba 2 4  --obs Bmag rmsB rmsB_ratio  --tshift  -lim ${lims[$il]}  --dir_data _pascal_/${struct}_${prex[$il]}  --wang 90.
    done
done


#EOF
