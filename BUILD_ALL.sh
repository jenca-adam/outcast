./PREPARE.sh # 312

for PYVERSION in 8 9 10 11;
	do echo "COMPILING FOR 3.$PYVERSION";
	OUTCAST_PYTHON="/home/adam/.local/py/3$PYVERSION/bin/python3.$PYVERSION" LD_LIBRARY_PATH="/home/adam/.local/py/3$PYVERSION/lib" ./PREPARE.sh;
done
