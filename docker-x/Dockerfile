#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# What we do:
# 1) We create an X environment for xpra.
#    Xpra works as an X server, which we'll need in order
#    to be able to generate figures with python.
# 2) install python packages in a Miniconda "environment".
#    The requirements are read from a .yml file, which is 
#    pulled from the web version of this Git repository.
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
FROM ubuntu:12.04
MAINTAINER Jimmy Masías "jimmy.ilws@gmail.com"

ENV HomeDocker /home/docker

RUN apt-get update

# Set the env variable DEBIAN_FRONTEND to noninteractive
ENV DEBIAN_FRONTEND noninteractive

# We need an X environment: xserver, xdm, flux box, roc-filer and ssh
RUN apt-get install -y xpra rox-filer ssh pwgen xserver-xephyr xdm fluxbox 
# just in case
RUN apt-get install -y sudo vim
RUN apt-get install -y expect git

# Set locale (fix the locale warnings)
RUN localedef -v -c -i en_US -f UTF-8 en_US.UTF-8 || :

# Copy the files into the container
#ADD ./docker-x /src

# TODO: need to re-direct this
#EXPOSE 22

# Add docker user (user:pass is docker:docker), in case we want to ssh with X:
RUN DOCKER_ENCRYPTED_PASSWORD=`perl -e 'print crypt(docker, "docker"),"\n"'` \
    && useradd -m -G sudo -d ${HomeDocker} -p "$DOCKER_ENCRYPTED_PASSWORD" -s /bin/bash docker


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++    A N A C O N D A    ++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# we'll need some files
ENV REPO_GUST=${HomeDocker}/seatos
#--- download && install Miniconda
WORKDIR ${HomeDocker}
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++ set python workspacce
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ENV Miniconda_sh=Miniconda-latest-Linux-x86_64.sh
# where to install Anaconda/Miniconda
ENV CONDADIR=/condadir
# name of the conda environment
ENV CONDAENV=work
# bashrc of the system (change according to Linux distribution)
ENV BASHRC_SYS=/etc/bash.bashrc

# this *has* to be done in one line in order to avoid 
# accumulating weight (by removing the downloaded
# file) to this image snapshot
RUN git clone --depth=1 https://github.com/jimsrc/seatos.git ${REPO_GUST} \
	&& wget -c http://repo.continuum.io/miniconda/${Miniconda_sh} \
	&& chmod +x ${Miniconda_sh} \
	&& ${REPO_GUST}/docker-x/conda_installer.sh ${HomeDocker}/${Miniconda_sh} ${CONDADIR} \
	&& rm ./${Miniconda_sh} \
	&& cp ${REPO_GUST}/docker-x/requirements/list_work.txt ${HomeDocker}/reqs.txt \
	&& cp ${REPO_GUST}/docker-x/requirements/export_work.yml ${HomeDocker}/reqs.yml \
	&& echo "export PATH=\"${CONDADIR}/bin:$PATH\"" >> ${BASHRC_SYS} \
    && tail ${BASHRC_SYS} \
	&& rm -rf ${REPO_GUST}


# update conda
RUN echo -e "\n [*] Updating conda...\n" \
	&& ${CONDADIR}/bin/conda install -c anaconda -y conda=4.3.23 \
	&& echo -e "\n [+] Finished updating conda!\n"

# install bunch of packages (this might take a while)
# NOTE: the "-c" arguments are the channels
# NOTE2: this creates an Anaconda environment, whose name is inside the .yml
RUN echo -e "\n [*] installing requirements...\n"\
    && ${CONDADIR}/bin/conda env create --name ${CONDAENV} -f ${HomeDocker}/reqs.yml \
    && echo -e "\n [+] Finished requirements installation!\n"
#RUN ${CONDADIR}/bin/conda env update -f ${HomeDocker}/reqs.yml \
    #&& echo -e "\n [+] Finished installing requirements!\n"

# useful for interaction && debugging
RUN ${CONDADIR}/bin/conda install --name ${CONDAENV} -c anaconda -y ipython
RUN ${CONDADIR}/bin/conda install --name ${CONDAENV} -c jjhelmus -y ipdb

# Start xdm and ssh services.
CMD ["/bin/bash"] #, "/src/startup.sh"]



#EOF
