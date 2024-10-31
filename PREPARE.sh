echo "Installing required packages..."
python -m pip install -r requirements.txt --break-system-packages >/dev/null || { echo -e "pip install failed with returncode $?\ncheck console for details"; exit 1; }
echo "Compiling cCore.so extension module..."
python setup.py build_ext -i >/dev/null || { echo -e "compile failed with returncode $?, are you on Windows?\ncheck console for details"; exit 1; }
rm -r build
echo "Compiling using pyinstaller..."
sh PYI_FREEZE.sh >/dev/null 2>/dev/null
sh PACK.sh
