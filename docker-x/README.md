<!--- Docker -->
# Docker 
---

You must build a Docker image (`ImageName1`) using this `Dockerfile` as:
```bash
docker build -t <ImageName1> <path/to/Dockerfile>
```

After building our Docker image with the above
instructions, run our image in a container:
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

Now you are ready to run Python inside the Docker container:
```bash
EXEC=/home/docker/miniconda2/bin/ipython # executable file (can also be a Bash script inside $XCONFIG)
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=1000:1000 -w ${HOME_GUST} <ImageNameN> $EXEC 
```

But if you need to run a script that needs a valid `DISPLAY` environment variable:
```bash
docker run -it --name ubuntuX2 --volume=${XCONFIG_HOST}:${XCONFIG_GUST} --user=1000:1000 -w ${HOME_GUST} <ImageNameN> /bin/bash
#--- and inside the container (start a DISPLAY in :10):
$HOME/src/config/docker-desktop -s 800x600 -d 10
DISPLAY=:10 ipython
#--- and inside IPython:
In [1]: run ./script.py  ## IT WORKS GREAT!!
```

<!--- EOF -->
