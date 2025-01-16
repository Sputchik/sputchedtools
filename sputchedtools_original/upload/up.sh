cd ../
rm -rf dist __pycache__ build sputchedtools.egg-info

# Build Cythonized wheel
CYTHONIZE=1 python3 setup.py -wn

# Build regular wheel
python3 setup.py -wn

# Build source distribution
python3 setup.py -sn
twine upload dist/*

rm -rf dist __pycache__ build sputchedtools.egg-info *.c MANIFEST.in