rm -rf dist __pycache__ build sputchedtools.egg-info

# Build regular wheel
python3 setup.py -wnsx
twine upload dist/*

rm -rf dist __pycache__ build sputchedtools.egg-info *.c MANIFEST.in