# This file creates a container that runs X11 and SSH services
# The ssh is used to forward X11 and provide you encrypted data
# communication between the docker container and your local 
# machine.
#
# Xpra allows to display the programs running inside of the
# container such as Firefox, LibreOffice, xterm, etc. 
# with disconnection and reconnection capabilities
#
# Xephyr allows to display the programs running inside of the
# container such as Firefox, LibreOffice, xterm, etc. 
#
# Fluxbox and ROX-Filer creates a very minimalist way to 
# manages the windows and files.
#
# Author: Roberto Gandolfo Hashioka
# Date: 07/28/2013


FROM ubuntu:12.04
MAINTAINER Jimmy Masías "jimmy.ilws@gmail.com"

ENV HomeDocker /home/docker

#RUN useradd -m -g sudo -s /bin/bash dummy
#USER dummy

RUN apt-get update

# Set the env variable DEBIAN_FRONTEND to noninteractive
ENV DEBIAN_FRONTEND noninteractive

# Installing the environment required: xserver, xdm, flux box, roc-filer and ssh
RUN apt-get install -y xpra rox-filer ssh pwgen xserver-xephyr xdm fluxbox 
# just in case
RUN apt-get install -y sudo vim
RUN apt-get install -y expect git


# Installing the apps: Firefox, flash player plugin, LibreOffice and xterm
# libreoffice-base installs libreoffice-java mentioned before
#RUN apt-get install -y libreoffice-base firefox libreoffice-gtk libreoffice-calc xterm

# Set locale (fix the locale warnings)
RUN localedef -v -c -i en_US -f UTF-8 en_US.UTF-8 || :

# Copy the files into the container
#ADD ./docker-x /src

# TODO: need to re-direct this
#EXPOSE 22

# Add docker user (user:pass is docker:docker) (TODO: password doen't seem to work!):
RUN DOCKER_ENCRYPYTED_PASSWORD=`perl -e 'print crypt(docker, "aa"),"\n"'`
RUN useradd -m -G sudo -d ${HomeDocker} -p "$DOCKER_ENCRYPYTED_PASSWORD" -s /bin/bash docker
#RUN sed -Ei 's/adm:x:4:/docker:x:4:docker/' /etc/group
#RUN adduser docker sudo


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++    A N A C O N D A    ++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# we'll need some files
#ADD ./docker-x/ ${HomeDocker}/src
ENV REPO_GUST=${HomeDocker}/seatos
#RUN git clone https://github.com/jimsrc/mean_profiles.ace.git ${REPO_GUST}

# switch to docker user
USER docker
#--- download && install Miniconda
WORKDIR ${HomeDocker}


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++ set python workspacce
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ENV Miniconda_sh=Miniconda-latest-Linux-x86_64.sh
# this *has* to be done in one line in order to avoid 
# accumulating weight (by removing the downloaded
# file) to this image snapshot
RUN git clone https://github.com/jimsrc/seatos.git ${REPO_GUST} \
	&& wget -c http://repo.continuum.io/miniconda/${Miniconda_sh} \
	&& chmod +x ${Miniconda_sh} \
	&& ${REPO_GUST}/docker-x/conda_installer.sh ${HomeDocker}/${Miniconda_sh} \
	&& rm ./${Miniconda_sh} \
	&& cp ${REPO_GUST}/docker-x/requirements/export_work.yml ${HomeDocker}/reqs.yml \
	&& echo 'export PATH="$HOME/miniconda2/bin:$PATH"' >> ${HomeDocker}/.bashrc \
	&& rm -rf ${REPO_GUST}

# update
RUN echo -e "\n [*] Updating conda...\n" \
	&& ${HomeDocker}/miniconda2/bin/conda install -c anaconda -y conda=4.3.23 \
	&& echo -e "\n [+] Finished updating conda!\n"

# install bunch of packages (this might take a while)
#RUN ${HomeDocker}/miniconda2/bin/conda env create --name work -f ${HomeDocker}/reqs.yml
RUN ${HomeDocker}/miniconda2/bin/conda install --file=${HomeDocker}/reqs.yml
# specific matplotlib && scipy (maybe this is not necessary)
#RUN ${HomeDocker}/miniconda2/bin/conda install -c anaconda -y matplotlib=1.5.1 scipy=0.19.0
# useful for interaction
RUN ${HomeDocker}/miniconda2/bin/conda install -c anaconda -y ipython 
RUN ${HomeDocker}/miniconda2/bin/conda install -c jjhelmus -y ipdb
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Start xdm and ssh services.
CMD ["/bin/bash"] #, "/src/startup.sh"]


#EOF
