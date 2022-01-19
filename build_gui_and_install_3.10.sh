# Remember to install pyenv Python with
# env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.0

# Build
clear
rm -rf build dist
pyinstaller --noconfirm --log-level=ERROR \
    --clean \
    --onefile \
    --windowed \
    --name Spotiripper \
    --paths ~/.pyenv/versions/3.10.0/envs/spotiripper_3.10/lib/python3.10/site-packages \
    --add-data settings.json:. \
    --add-data spotiripper.png:. \
    --icon spotiripper.png \
    --debug imports \
    spotiripper.py

# --hidden-import plyer.platforms.macosx.notification \
# --paths ~/.pyenv/versions/spotiripper/ \
# --hidden-import PySide6 \
# --hidden-import PySide6.QtWidgets \
# --hidden-import PySide6.QtGui \
# --hidden-import PySide6.QtCore \

# Install
cp -R dist/Spotiripper.app /Applications/
