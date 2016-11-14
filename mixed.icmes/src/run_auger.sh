#!/bin/bash
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_

group=(lo mid hi)
lims=('100. 375.' '375. 450.' '450. 3000.')

# splitted profiles
for i in $(seq 0 1 2); do
    OUT=./out.auger_${group[$i]}
    ./splitted.py -- --left $LEFT  --right $RIGHT  --plot $OUT  --lim ${lims[$i]}
done

# global profile
OUT=./out.auger_all
./splitted.py -- --left $LEFT  --right $RIGHT  --plot $OUT
#EOF
