if [ -z "$OUTCAST_PYTHON" ]; then
	OUTCAST_PYTHON=$(which python3);
fi;
echo "Python is: $OUTCAST_PYTHON";
echo "Installing required packages..."
$OUTCAST_PYTHON -m pip install -r requirements.txt >/dev/null || { echo -e "pip install failed with returncode $?\ncheck console for details"; exit 1; }
echo "Compiling cCore.so extension module..."
$OUTCAST_PYTHON setup.py build_ext -i >/dev/null || { echo -e "compile failed with returncode $?, are you on Windows?\ncheck console for details"; exit 1; }
rm -r build
echo "Compiling using pyinstaller..."
env OUTCAST_PYTHON=$OUTCAST_PYTHON sh PYI_FREEZE.sh >/dev/null 
sh PACK.sh
