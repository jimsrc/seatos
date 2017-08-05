<!--- Docker -->
# Docker (only for Linux)

In order to run the present work in a Docker container, you can directly pull the built image as:
```bash
docker pull jimjdocker/seatos:v1
```
Or you can build the Docker image (say `ImageName`) using this [Dockerfile](Dockerfile) as:
```bash
# Note that <Dockerfile-directory> must be the absolute path 
# to the directory where the Dockerfile is placed (not the path
# to the Dockerfile itself)
docker build --rm -t <ImageName> <Dockerfile-directory>
# this might take ~20min the first time
```

Now you are ready to run Python inside a Docker container:
```bash
HOME_GUST=/home/docker
XCONFIG_HOST=<this-repository>/docker-x
XCONFIG_GUST=${HOME_GUST}/src
EXEC=/condadir/bin/ipython # (can be replaced by any executable file)
docker run -it --rm --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=$UID:${GID} -w ${HOME_GUST} <ImageName> $EXEC 
```

---
But if you need to run a script that needs a valid `DISPLAY` environment variable:
```bash
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=1000:1000 -w ${HOME_GUST} <ImageNameN> /bin/bash
#--- and inside the container (start a DISPLAY in :10):
$HOME/src/config/docker-desktop -s 800x600 -d 10
DISPLAY=:10 ipython
#--- and inside IPython:
In [1]: run ./script.py  ## IT WORKS GREAT!!
```

---
<!--- THIS IS TESTED! -->
## Reproduction of A&A figures
The script [rundocker.sh](rundocker.sh) has the settings to run scripts that reproduce 
some figures of the A&A paper.
Just:
```bash
cd docker-x
./rundocker.sh <absolute-output-directory>
```
### Remarks:
* the above script needs a valid `REPO_HOST` environment variable, which has to be the path to 
this Git repository (in this commit).
* all variables with suffixes `_HOST` and `_GUST` refers to paths in the host ("real") and 
guest (i.e. inside the Docker container) systems.
* the `DOCKER_IMAGE` env variable refers to the Docker image you'll execute.
* the section "List of data sources" (inside `rundocker.sh`) defines paths to input 
filenames (which have prefix `fnm_`) that exist in the host system. Make sure to correct 
those if necessary.
* this script takes as 1st argument a path where output files will be placed. In case such path
already exists and is not empty, a backup will be made using the current date and time as suffix
for the backup directory (see `_dirbckp` variable).
* If the variable `ProvideExtractedData` equals `1`, the script won't perform data extraction.
Instead, the paths given by `LEFT_HOST` and `RIGHT_HOST` will be used by the 
script [docker_test.sh](docker_test.sh) to build mixed profiles.
If the variable `ProvideExtractedData` equals `0`, the script will perform data extraction from the
ACE and CR-detector datasets, and later the mixed profiles will be built. Note that for the later option,
you'll have to modify the `LEFT` and `RIGHT` variable by hand in [docker_test.sh](docker_test.sh).
* you can use these [LEFT](../etc/tmp_left) and [RIGHT](../etc/tmp_right) directories as input for
[this](../mixed.icmes/src/splitted.py) script (which is called by the chain [script1](docker_test.sh) 
--> [script2](../tests/auger.solphys.sh) --> [script3](../mixed.icmes/src/splitted.py))
They are set with the variables `LEFT_HOST` and `RIGHT_HOST`.


<!--- EOF -->
