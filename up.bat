@echo off
rmdir /S /Q dist build *.egg-info __pycache__

:: Build Cythonized wheel
call devcmd
set CYTHONIZE=1
python -m build -wn
set CYTHONIZE=

:: Build regular wheel 
python -m build -wn

:: Build source distribution
python -m build -sn
twine upload dist/*

rmdir /S /Q dist build *.egg-info __pycache__ *.c *.in