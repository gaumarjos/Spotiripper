#!/usr/bin/env bash

# Remember to install pyenv Python with
# env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.0

lib_location=~/.pyenv/versions/3.10.0/envs/spotiripper_3.10/lib/python3.10/site-packages/

# Build
clear
echo "lib_location:" $lib_location
rm -rf build dist
rm spotiripper.spec

pyinstaller --noconfirm --log-level=WARN --clean --onefile --windowed \
  --name Spotiripper \
  --paths $lib_location \
  --add-data settings.json:. \
  --add-data log.csv:. \
  --add-data spotiripper.png:. \
  --icon spotiripper.png \
  --hidden-import PySide2.QtQml \
  --hidden-import PySide2.QtWidgets \
  --hidden-import PySide2.QtGui \
  --hidden-import PySide2.QtCore \
  --hidden-import numpy \
  --debug imports \
  main_gui.py

# --hidden-import plyer.platforms.macosx.notification \

# Still not working with 6. It asks for a QtDBus but when added as as hidden import it cannot include it.
#  --hidden-import PySide6.QtQml \
#  --hidden-import PySide6.QtDBus \
#  --hidden-import PySide6.QtWidgets \
#  --hidden-import PySide6.QtGui \
#  --hidden-import PySide6.QtCore \


#  --paths ~/.pyenv/versions/spotiripper_3.6.5/ \

# Install
cp -R dist/Spotiripper.app /Applications/
