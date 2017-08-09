# SEATOS
### Superposed Epoch Analysis TOolkit for Space physics

---
## Intro:

This is a collection of Python (a little bit of Cython too) scripts to:

   * build average time profiles: the average being made along similar events 
     occurring in different physical intervals of time.
     See the [one.structure/src](one.structure/src) directory for source codes; in particular the [sea_splitted.py](one.structure/src/sea_splitted.py) script.

   * calculate average values of different observables: these observables are 
     associated to the mentioned events.
<!--- TODO: referenciar directorio -->

   * evaluate a semi-empirical model of Galactic Cosmic Rays to Neutron monitor 
     data, using interplanetary measurements as input. 
     See the [nCR-model](etc/n_CR) directory; in particular the [apply_model.py](etc/n_CR/individual/apply_model.py) script.

   * characterize Forbush decrease parameters, such as: recovery time (using 
     completely automatic algorithm, which also determines the best time interval
     to fit), the relative amplitude, and offset of the post-recovery CR-flux 
     respect to the pre-shock CR-flux.
<!--- TODO: referenciar directorio -->


---
### Related publications using this tool:
* _"[Superposed epoch study of ICME sub-structures near Earth and their effects on Galactic cosmic rays](https://www.aanda.org/articles/aa/abs/2016/08/aa28571-16/aa28571-16.html)"_, 
J. J. Masías-Meza, S. Dasso, P. Démoulin, L. Rodriguez and M. Janvier,
Astronomy & Astrophysics (ISSN 0004-6361), Vol. 592, A118. 
Published on Aug/2016.
* _"[Typical Profiles and Distributions of Plasma and Magnetic Field Parameters in Magnetic Clouds at 1 AU](https://link.springer.com/article/10.1007/s11207-016-0955-5)"_, 
L. Rodriguez, J. J. Masías-Meza, S. Dasso, P. Démoulin, A. N. Zhukov, A. M. Gulisano, M. Mierla, E. Kilpua, M. West, D. Lacatus, A. Paraschiv, M. Janvier,
Solar Physics (ISSN 0038-0938), Vol. 291, Issue 7, pp.2145-2163.
Published on July/2016.


---
## Mean profiles:

Tweaked script that uses pre-defined time-windows of Interplanetary Coronal Mass
Ejections (see [Richardson's catalog](http://www.srl.caltech.edu/ACE/ASC/DATA/level3/icmetable2.htm)), to generate mean profiles (along with its standard deviation and median 
values).
As example, calculate the mean profile of a collection of ICME's sheath:
```bash
# path to input files
ACE=~/data_ace/64sec_mag-swepam/ace.1998-2015.nc
MURDO=~/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat
AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
HSTS=$AUGER_REPO/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5
SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5

# run script
cd one.structure/src
./sea_splitted.py -- --ace $ACE --mcmurdo $MURDO --avr $AVR --rich_csv $RICH_CSV \
    --dir_plot ../plots3 --dir_data ../ascii3 --suffix _out_ \
    --icme_flag 0.1.2.2H  --struct sh.i
```

---
### Technical remarks:
* the more busy routines for the data processing are inside the `events_mgr` class (see the library [shared_funcs.py](shared_lib/shared_funcs.py)).
* for each `--inp_SOMETHING` argument that the [sea_splitted.py](one.structure/src/sea_splitted.py) script recieves, there is a `_data_SOMETHING` class defined in the [readers.py](shared_lib/readers.py) file.
* In case you need to process another data set (let's call it `NEWDATA`), you need to implement a way to access the variables of interest inside the file by writing a new class named `_data_NEWDATA` in [readers.py](shared_lib/readers.py), and a respective `argparse` argument in [sea_splitted.py](one.structure/src/sea_splitted.py) that accepts the argument `--inp_NEWDATA`.


---
## Docker
For more reproducibility, a [Dockerfile](docker-x/Dockerfile) has been created in order to 
be able to run the present work inside a Docker container.
The build steps are detailed inside that file, which basically grabs an Ubuntu 12.04 "environment" 
and installs an X server to provide a valid `DISPLAY` environment variable for Python later.
This image is already built and uploaded to [DockerHub](https://hub.docker.com), and can be pulled 
from a bash terminal like so:
```bash
# this might take a while
docker pull jimjdocker/seatos:v1
```

Alternatively, this image can be built in your host like:
```bash
# Note that <Dockerfile-directory> must be the absolute path 
# to the directory where the Dockerfile is placed (not the path
# to the Dockerfile itself)
docker build --rm -t <ImageName> <Dockerfile-directory>
# this might take ~20min the first time
```

For execution inside Docker (for more details, see the other [README](docker-x/README.md)):
```bash
HOME_GUST=/home/docker
XCONFIG_HOST=$ASO/icmes_richardson/data/mean_profiles/ace_docker/docker-x
XCONFIG_GUST=${HOME_GUST}/src
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=1000:1000 -w ${HOME_GUST} <ImageNameN> /bin/bash

#--- now inside the container (start a DISPLAY in :10):
$HOME/src/config/docker-desktop -s 800x600 -d 10
DISPLAY=:10 ipython

#--- and now inside IPython:
In [1]: run ./script.py  ## IT WORKS GREAT!!
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
