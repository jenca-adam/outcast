if [ ! -d "dist/cast_away" ]; then
	echo "Please run PYI_FREEZE.sh first";
	exit 1;
fi
echo "Preparing pack operation..."
rm dist/CAST_AWAY*tar.gz
FN="CAST_AWAY.$(cat files/VERSION).$(find dist/cast_away -type f | grep -o "cCore.*so" | sed 's/\./ /g' | awk '{print $2}').tar"
echo "Packing with tar..."
echo "Filename: dist/$FN"
cd dist
tar -cf $FN  *
echo "Gzipping..."
yes | gzip  -f $FN
echo "Cleaning up..."
rm -r cast_away
for i in *.tar.gz; do
	mv $i ../gzipped_dist;
done
cd ..
rm -r dist;
