rm -f dist/*
rm -rf __pycache__
rm -rf build
rm -rf sputchedtools.egg-info

python3 setup.py sdist bdist_wheel
twine upload dist/*

rm -f dist/*
rm -rf __pycache__
rm -rf build
rm -rf sputchedtools.egg-info