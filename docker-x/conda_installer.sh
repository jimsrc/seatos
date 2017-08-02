#!/bin/bash

# the Anaconda/Miniconda installer is interactive, so we make
# a programatic version of that installation

# installer executable
EXE=$1          # 1st argument
# where to install Anaconda
CondaDir=$2     # 2nd argument


# non-interactive installer of Miniconda
$EXE 1> /dev/null <<-EOF
q
yes
$CondaDir
EOF


#EOF
