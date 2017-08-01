#!/bin/bash

# non-interactive installer of Miniconda
$1 1> /dev/null <<-EOF
q
yes
EOF
