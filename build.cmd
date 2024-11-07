rmdir /S /Q dist
rmdir /S /Q build
rmdir /S /Q sputchedtools.egg-info
rmdir /S /Q __pycache__

python setup.py sdist bdist_wheel
twine upload dist/*

rmdir /S /Q dist
rmdir /S /Q build
rmdir /S /Q sputchedtools.egg-info
rmdir /S /Q __pycache__