@echo off

set "origin=%CD%"
cd "%~dp0../"

:: Build Cythonized wheel
:: call devcmd
:: set CYTHONIZE=1
:: python -m build -wn
:: set CYTHONIZE=

:: Build regular wheel
python -m build -wnsx

echo.
twine upload dist/*
rmdir /S /Q dist

for /D %%G in (".\src\*egg-info") do rmdir /S /Q "%%G"
rmdir /S /Q  build
:: del /S /Q sputchedtools.c MANIFEST.in
cd "%origin%"