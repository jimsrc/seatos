#!/bin/bash
export LEFT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_sh.i_
export RIGHT=$MEAN_PROFILES_ACE/one.structure/src/out.auger/MCflag0.1.2.2H/woShiftCorr/_i_
export PREFIX=MCflag0.1.2.2H_2before.4after_fgap0.5_WangNaN


vname=Auger_BandMuons
fname_fig=(./${vname}_fast.png ./${vname}_all.png)
arglim=('--lim 450. 3000.' '')

#--- run
for i in $(seq 0 1 1); do
    ./apply_model.py -- --left $LEFT  --right $RIGHT  --prefix $PREFIX  --suffix CRs.${vname}  --fig "${fname_fig[$i]}"  ${arglim[$i]}
done


#EOF
