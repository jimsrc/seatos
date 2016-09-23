# run


Run `n_CR` model with command-line arguments:

```bash
export LEFT=$MEAN_PROFILES_ACE/sheaths.icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_
export RIGHT=$MEAN_PROFILES_ACE/icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_
export PREFIX=MCflag0.1.2.2H_2before.4after_fgap0.2_WangNaN
./apply_model.py -- --left $LEFT  --right $RIGHT  --prefix $PREFIX  --suffix CRs.Auger_scals  --lim 100. 375.  --fig ../figs/indiv/test.png
```
