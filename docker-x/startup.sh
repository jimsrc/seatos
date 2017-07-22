#!/bin/bash

## Add docker user and generate:
#DOCKER_PASSWORD=docker #`pwgen -c -n -1 12`
#DOCKER_ENCRYPYTED_PASSWORD=`perl -e 'print crypt('"$DOCKER_PASSWORD"', "aa"),"\n"'`
#useradd -m -d /home/docker -p $DOCKER_ENCRYPYTED_PASSWORD -s /bin/bash docker
#sed -Ei 's/adm:x:4:/docker:x:4:docker/' /etc/group
#adduser docker sudo

# Copy the config files into the docker directory
cd /src/config/ && sudo -u docker cp -R .[a-z]* [a-z]* /home/docker/

# restarts the xdm service
/etc/init.d/xdm restart

#EOF
