if [ -z "$OUTCAST_PYTHON" ]; then
	OUTCAST_PYTHON=$(which python3);
fi;
yes|$OUTCAST_PYTHON -m PyInstaller freeze.spec --noconfirm
rm -r build
