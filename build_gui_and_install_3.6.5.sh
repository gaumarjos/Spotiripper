# To install an older python version with pyenv on BigSur
# LDFLAGS="-L$(brew --prefix zlib)/lib -L$(brew --prefix bzip2)/lib" PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install --patch 3.6.5 < <(curl -sSL https://github.com/python/cpython/commit/8ea6353.patch\?full_index\=1)
# https://dev.to/kojikanao/install-python-3-7-3-6-and-3-5-on-bigsure-with-pyenv-3ij2

# Remember to install pyenv Python with
# env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.6.5

# Build
clear
rm -rf build dist
pyinstaller --noconfirm --log-level=ERROR \
    --clean \
    --onefile \
    --windowed \
    --name Spotiripper \
    --paths ~/.pyenv/versions/spotiripper_3.6.5/ \
    --paths ~/.pyenv/versions/3.6.5/envs/spotiripper_3.6.5/lib/python3.6/site-packages/ \
    --add-data settings.json:. \
    --add-data spotiripper.png:. \
    --icon spotiripper.png \
    --hidden-import PySide2 \
    --hidden-import PySide2.QtWidgets \
    --hidden-import PySide2.QtGui \
    --hidden-import PySide2.QtCore \
    --debug imports \
    spotiripper.py

# --hidden-import plyer.platforms.macosx.notification \

# Install
cp -R dist/Spotiripper.app /Applications/
