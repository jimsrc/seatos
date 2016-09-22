# SEATOS
### Superposed Epoch Analysis TOolkit for Space physics

---

1. This is a collection of Python (a little bit of Cython too) scripts to:
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
