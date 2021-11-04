# To install an older python version with pyenv on BigSur
# LDFLAGS="-L$(brew --prefix zlib)/lib -L$(brew --prefix bzip2)/lib" PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install --patch 3.6.5 < <(curl -sSL https://github.com/python/cpython/commit/8ea6353.patch\?full_index\=1)
# https://dev.to/kojikanao/install-python-3-7-3-6-and-3-5-on-bigsure-with-pyenv-3ij2

# Remember to install pyenv Python with
# env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.9.7

# Build
clear
rm -rf build dist
pyinstaller --noconfirm --log-level=ERROR \
    --clean \
    --onefile \
    --nowindowed \
    --name spotiripper \
    --paths ~/.pyenv/versions/spotiripper/ \
    --paths ~/.pyenv/versions/3.9.7/envs/spotiripper/lib/python3.9/site-packages/ \
    main.py

# Install
cp dist/spotiripper /usr/local/bin
