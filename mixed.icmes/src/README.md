# Build composed mean-profile:

Run:
```bash
## can be low, mid, or high
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/test/MCflag0.1.2.2H/woShiftCorr/_auger_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/test/MCflag0.1.2.2H/woShiftCorr/_auger_i_
./splitted.py -- --Vsplit 375. 450.  --left $LEFT  --right $RIGHT  --plot ../auger_mid  --group mid  
```
Note that in the directories $LEFT and $RIGHT, we have the data files associated to the 3 different groups!.
