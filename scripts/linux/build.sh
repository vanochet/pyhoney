echo "Creating virtual environment"
python3 >/dev/null -m venv venv
export ENV=./venv/bin
$ENV/pip >/dev/null install pyinstaller parglare
echo "Building binaries"
$ENV/pyinstaller >/dev/null --nowindow --strip --upx-dir=bin -y -F --log-level=ERROR src/hny.py
$ENV/pyinstaller >/dev/null --nowindow --strip --upx-dir=bin -y -F --log-level=ERROR src/hna/hna.py
chmod -R +x ./bin
echo "Repairing file system"
cp >/dev/null 2>&1 dist/hny bin/hny
cp >/dev/null 2>&1 dist/hna bin/hna
echo "Clearing temporary files"
rm >/dev/null 2>&1 -rf build dist venv
unlink >/dev/null 2>&1 hny.spec
unlink >/dev/null 2>&1 hna.spec
echo "Done build"
