#!/bin/bash
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_

group=low
OUT=./out.auger_${group}
./splitted.py -- --left $LEFT  --right $RIGHT  --plot $OUT  --group $group


#EOF
