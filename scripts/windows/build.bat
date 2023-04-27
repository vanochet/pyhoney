@echo off
echo Creating virtual environment
py -m venv venv
venv\scripts\pip install pyinstaller parglare
echo Building binaries

venv\scripts\pyinstaller --nowindow  --upx-dir=bin -y -F --log-level=ERROR src/hny.py
venv\scripts\pyinstaller --nowindow  --upx-dir=bin -y -F --log-level=ERROR src/hna/hna.py

echo Done build
pause