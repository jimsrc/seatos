#!/bin/bash
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_
OUTDIR=./_auger.solphys2_

./fd_all.py --pdb -- --plot $OUTDIR  -right $RIGHT  -left $LEFT -ylim_B.ACE 4.5 13.0

#./fd_all.py --pdb -- --plot ./_auger.solphys2_  -right $RIGHT  -left $LEFT  -lim 375. 450.
./fd_all.py --pdb -- --plot $OUTDIR  -right $RIGHT  -left $LEFT -lim 450. 3000. \
    -ylim_B.ACE 4.5 13.0 -ylim_CRs.Auger_BandScals -0.8 0.25 -ylim_CRs.Auger_BandMuons -0.8 0.25 -ylim_CRs.Auger_scals -0.8 0.25
#EOF
