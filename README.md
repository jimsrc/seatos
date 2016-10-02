# SEATOS
### Superposed Epoch Analysis TOolkit for Space physics

---
# Intro:

This is a collection of Python (a little bit of Cython too) scripts to:

   * build average time profiles: the average being made along similar events 
     occurring in different physical intervals of time.
     See the [icmes](icmes/src), [sheath.icmes](sheaths.icmes/src) directories for instance.
<!--- referenciar directorio -->

   * calculate average values of different observables: these observables are 
     associated to the mentioned events.
<!--- referenciar directorio -->

   * evaluate a semi-empirical model of Galactic Cosmic Rays to Neutron monitor 
     data, using interplanetary measurements as input. 
     See [nCR-model](etc/n_CR) directory.

   * characterize Forbush decrease parameters, such as: recovery time (using 
     completely automatic algorithm, which also determines the best time interval
     to fit), the relative amplitude, and offset of the post-recovery CR-flux 
     respect to the pre-shock CR-flux.
<!--- referenciar directorio -->

---
# Mean profiles:

Tweaked script that that uses pre-defined time-windows of Interplanetary Coronal Mass
Ejections, to generate mean profiles (along with its standard deviation and median 
values).
It uses the `events_mgr` class (see [shared functions](link here) directory) to generate, to parse 
to it the border times given by [Richardson's List](link here).

As example, calculate the mean profile of a collection of ICME's sheath:

```bash
# path to input files
export ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
export MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
export SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5
# run script
./sea_splitted.py -- --ace $ACE --mcmurdo $MURDO --avr $ASO/icmes_richardson/data/rich_events2_ace.nc --rich_csv $ASO/icmes_richardson/RichardsonList_until.2016.csv --auger_hsts $AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5 --auger_scls $PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5 --dir_plot ../plots3 --dir_data ../ascii3 --suffix _auger_ --icme_flag 0.1.2.2H  --struct sh.i
```



---
### TODO:

- [ ] Unify code, so that we obtaint the same output of the different 
      scripts written for the different structures can be executed 
      using one single script via command-line arguments.

- [ ] automate the search of best intervals of the fit-parameters, for
      the brute-force method.

- [ ] make the `extrac_struct.py` use the same routine as `events_mgr.rebine()`,
      instead of using the repeated code `events_mgr.collect_data()`.

- [ ] make the `structure` argument smarter in `events_mgr.__init__()`.

- [ ] script to make shorter the distance between getting the data from 
      the Neutron Monitor Database ([NMDB](http://www.nmdb.eu/?q=node/8)), and
      build the input file that uses the scripts for analysis.

- [ ] read .hdf (HDF4 format) files with Python. There's no well documented 
      material in this direction!! Alternatives are:
      pyhdf, pynio, python-hdf4, etc.
      This is important to handle ACE data. 
      For now, we are following the converting-ASCII-to-HDF5 way.

- [ ] Is there any way to better optimize the brute-force method? 
      See the [nCR-model](etc/n_CR) directory.

<!--- EOF -->
