# Remember to install pyenv Python with
# env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.9.7

# Build
clear
rm -rf build dist
pyinstaller --noconfirm --log-level=ERROR \
    --clean \
    --onefile \
    --windowed \
    --name Spotiripper \
    --paths ~/.pyenv/versions/spotiripper/ \
    --paths ~/.pyenv/versions/3.9.7/envs/spotiripper/lib/python3.9/site-packages/ \
    --add-data settings.json:. \
    --add-data spotiripper.png:. \
    --icon spotiripper.png \
    --hidden-import PySide6 \
    --hidden-import PySide6.QtWidgets \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtCore \
    --debug imports \
    spotiripper.py

# --hidden-import plyer.platforms.macosx.notification \

# Install
cp -R dist/Spotiripper.app /Applications/
