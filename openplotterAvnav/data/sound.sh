#! /bin/bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
gain=$(python3 -c "import sys;print(float(sys.argv[1].replace('%',''))/100.0)" $1)
/usr/bin/cvlc --play-and-exit --gain=$gain $2
