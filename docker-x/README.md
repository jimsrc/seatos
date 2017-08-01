<!--- Docker -->
# Docker 
---

You must build a Docker image (say `ImageName1`) using this [Dockerfile](Dockerfile) as:
```bash
docker build -t <ImageName1> --build-arg REPO_HOST=<root-path-of-this-repository> <path/to/Dockerfile>
```

After building our Docker image with the above
instructions, run the `ImageName1` in a container:
```bash
HOME_GUST=/home/docker
XCONFIG_HOST=<this-repository>/docker-x
XCONFIG_GUST=${HOME_GUST}/src
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} <ImageName1> /bin/bash
```

Then, while the container is running, install some other stuff inside 
the container.
NOTE: for each stuff you install, it's recommended to commit the
changes and then stop and remove the container; for the next installation, 
you should run the last commited image.
```bash
# install Miniconda, then:
conda env create --name work -f $HOME/src/requirements/export_work.yml
conda install -c anaconda ipython
conda install -c anaconda matplotlib=1.5.1 scipy=0.19.0

# the last commit should be:
docker commit -m "conda install -c anaconda matplotlib=1.5.1 scipy=0.19.0" ubuntuX2 <ImageNameN>
```
<!--- TODO: we can include these commands in the Docker file by
      adding the '-y' flag to 'conda install'.            
-->

Now you are ready to run Python inside the Docker container:
```bash
EXEC=/home/docker/miniconda2/bin/ipython # executable file (can also be a Bash script inside $XCONFIG)
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=1000:1000 -w ${HOME_GUST} <ImageNameN> $EXEC 
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
