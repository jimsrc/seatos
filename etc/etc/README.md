# misc utils

---
To extract data from specific events:
```bash
./extract_struct.py -- --tshift -dd ./tt -lim 550. 3001. --icme_flag 2 --ini shock --end ini_mc -ba 0. 0.
# example for scalers
export SCLS=$PAO/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5 # old-version scalers
export SCLS=$AUGER_REPO/scl.build_final/test.h5 # new-version scalers
export RICH_CSV=$ASO/icmes_richardson/RichardsonList_until.2016.csv
export AVR=$ASO/icmes_richardson/data/rich_events2_ace.nc
./extract_struct.py -- -avr $AVR -rich $RICH_CSV --inp_name Auger_scals  --input $SCLS  -dd ./scls_old2  -lim 100. 3000.  --icme_flag 0.1.2.2H  --struct i  -ba 0 0  --obs CRs
# for more info:
./extract_struct.py -- -h
```

<!--- EOF -->
