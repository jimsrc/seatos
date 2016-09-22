# Build mean-profiles in icme

Run:
```bash
# path to input files
export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
export SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5
# now execute
./sea_splitted.py -- --ace $ACE --mcmurdo $MURDO --avr $AVR --rich_csv $RICH_CSV --auger_hsts $HSTS --auger_scls $SCLS --dir_plot ../plots3 --dir_data ../ascii3 --suffix _auger_ --icme_flag 0.1.2.2H
```
