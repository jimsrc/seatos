# Build mean-profiles in icme-sheath

Run:
```bash
# path to input files
export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
# Jan/2006-Dec/2013 version of scalers (hdf5 file)
export SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5
# Jan/2006-Dec/2015 version of scalers (very different hdf5 structure inside!)
export SCLS=$AUGER_REPO/scl.build_final/test.h5
# now execute
./sea_splitted.py -- --ace $ACE --mcmurdo $MURDO --avr $AVR --rich_csv $RICH_CSV --auger_hsts $HSTS --auger_scls $SCLS --dir_plot ../plots3 --dir_data ../ascii3 --suffix _auger_ --icme_flag 0.1.2.2H --struct sh.i
# to reproduce A&A paper
./sea_splitted.py -- -ace $ACE -ace1sec 0 -murdo 0  -avr $AVR  --rich_csv $RICH_CSV -ahs 0  -ahm 0 -as 0 --dir_plot ./test  --dir_data ./test  --suffix _sh.mc_  --icme_flag 2  --struct sh.mc  --wang 1 90.  --Vsplit 450. 550.  --tshift
```
Note that, you can use `0` for `--ace` and `--mcmurdo`, to avoid processing them.


---
# for hegea:
```bash
export RICH_CSV=./data/RichardsonList_until.2016.csv
export AVR=./data/rich_events2_ace.nc
export ACE=$HOME/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export ACE1sec=$HOME/data_ace/mag_data_1sec   # directory
./sea_splitted.py -- -ace 0  -ace1sec $ACE1sec  -murdo 0  -avr $AVR --rich_csv $RICH_CSV -ahm 0  -ahs 0  -as 0  --dir_plot ./test2 --dir_data ./test2 --suffix _test_  --icme_flag 0.1.2.2H  --struct i
# to reproduce A&A figs, but now using ACE1sec `data_name`:
./sea_splitted.py -- -ace $ACE  -ace1sec $ACE1sec  -murdo 0  -avr $AVR --rich_csv $RICH_CSV -ahm 0  -ahs 0  -as 0  --dir_plot ./mc_ace --dir_data ./mc_ace --suffix _sh.mc_  --icme_flag 2  --struct sh.mc  --tshift  --Vsplit 450. 550.  --wang 1 90.
```
