#!/bin/bash
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_

# create output directory
export OUT=./_auger.solphys3_ && mkdir $OUT

# script exe
EXE=$MEAN_PROFILES_ACE/etc/etc/fd_all.py

# Run the global averages
$EXE --pdb -- --plot $OUT  -right $RIGHT  -left $LEFT -ylim_B.ACE 4.5 13.0

# Run the splitted way
# the '-lim' argument is a couple of number setting the lower and upper limit for the Vsw speed.
$EXE --pdb -- --plot $OUT  -right $RIGHT  -left $LEFT -lim 450. 3000. -ylim_B.ACE 4.5 13.0 -ylim_CRs.Auger_BandScals -0.8 0.25 -ylim_CRs.Auger_BandMuons -0.8 0.25 -ylim_CRs.Auger_scals -0.8 0.25
#EOF
