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
MAINTAINER Roberto G. Hashioka "roberto_hashioka@hotmail.com"

#RUN useradd -m -g sudo -s /bin/bash dummy
#USER dummy

RUN apt-get update

# Set the env variable DEBIAN_FRONTEND to noninteractive
ENV DEBIAN_FRONTEND noninteractive

# Installing the environment required: xserver, xdm, flux box, roc-filer and ssh
RUN apt-get install -y xpra rox-filer ssh pwgen xserver-xephyr xdm fluxbox sudo vim


# Installing the apps: Firefox, flash player plugin, LibreOffice and xterm
# libreoffice-base installs libreoffice-java mentioned before
#RUN apt-get install -y libreoffice-base firefox libreoffice-gtk libreoffice-calc xterm

# Set locale (fix the locale warnings)
RUN localedef -v -c -i en_US -f UTF-8 en_US.UTF-8 || :

# Copy the files into the container
ADD ./docker-x /src

EXPOSE 22

# Add docker user (user:pass is docker:docker):
RUN DOCKER_ENCRYPYTED_PASSWORD=`perl -e 'print crypt(docker, "aa"),"\n"'`
RUN useradd -m -G sudo -d /home/docker -p "$DOCKER_ENCRYPYTED_PASSWORD" -s /bin/bash docker
#RUN sed -Ei 's/adm:x:4:/docker:x:4:docker/' /etc/group
#RUN adduser docker sudo

# Start xdm and ssh services.
CMD ["/bin/bash", "/src/startup.sh"]


#EOF
