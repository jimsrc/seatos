#!/bin/bash
#--- paths
export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
export SCLS=$AUGER_REPO/scl.build_final/test_iv.h5 # newest version

vsplit='375. 450.' # to define the partition in 3 groups
for struct in sh.i i; do
    dir_out=./out.auger
    #--- run for the 3 subgroups && the global one
    ./sea_splitted.py -- -ace 0 -ace1sec 0 -murdo 0 -avr $AVR --rich_csv $RICH_CSV -ahs $HSTS -ahm $HSTS -as $SCLS --dir_plot $dir_out --dir_data $dir_out --suffix _${struct}_ --icme_flag 0.1.2.2H --struct $struct --Vsplit $vsplit 
    #if [ $?!=0 ]; then break; fi # break bash script on python crash
    echo " --> exit status: " $?
done

#EOF
